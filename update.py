import sys
import requests
import os
import urllib
import json
import zipfile
import argparse
import time
import threading
import shutil
import _pickle as cPickle
from collections import namedtuple
from multiprocessing.pool import ThreadPool
from urllib.parse import urlsplit

# default parameters
defaults = dict(
    thread_count=10,
    buffer_size=500 * 1024,
    block_size=1000 * 1024)

# global lock
lock = threading.Lock()

def new_download(url, file_path):
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])

    # 这重要了，先看看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    # 显示一下下载了多少   
    print(temp_size)
    print(total_size)
    # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}  
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers)

    # 下面写入文件也要注意，看到"ab"了吗？
    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()  # 避免上面\r 回车符


def get_file_info(url):  # 发送请求读取要下载的文件大小
    class HeadRequest(urllib.request.Request):
        def get_method(self):
            return "HEAD"
    res = urllib.request.urlopen(HeadRequest(url))
    res.read()
    headers = dict(res.headers)
    size = int(headers.get('Content-Length', 0))
    lastmodified = headers.get('last-modified', '')
    name = None
    if 'content-disposition'in headers:
        name = headers['content-disposition'].split('filename=')[1]
        if name[0] == '"' or name[0] == "'":
            name = name[1:-1]
    else:
        name = os.path.basename(urlsplit(url)[2])
    return FileInfo(url, name, size, lastmodified)

FileInfo = namedtuple('FileInfo', 'url name size lastmodified')

def download(url, output,  # 下载
             thread_count=defaults['thread_count'],
             buffer_size=defaults['buffer_size'],
             block_size=defaults['block_size']):
    file_info = get_file_info(url)
    if output is None:
        output = file_info.name
    workpath = '%s.ing' % output
    infopath = '%s.inf' % output
    blocks = []
    if os.path.exists(infopath):
        _x, blocks = read_data(infopath)
        if (_x.url != url or
                _x.name != file_info.name or
                _x.lastmodified != file_info.lastmodified):
            blocks = []
    if len(blocks) == 0:
        if block_size > file_info.size:
            blocks = [[0, 0, file_info.size]]
        else:
            block_count, remain = divmod(file_info.size, block_size)
            blocks = [[i * block_size, i * block_size,
                       (i + 1) * block_size - 1] for i in range(block_count)]
            blocks[-1][-1] += remain
        with open(workpath, 'wb') as fobj:
            fobj.write(''.encode(encoding='UTF8'))
    print('Downloading %s' % url)
    threading.Thread(target=_monitor, args=(
        infopath, file_info, blocks)).start()
    with open(workpath, 'rb+') as fobj:
        args = [(url, blocks, fobj, buffer_size)
                for i in range(len(blocks)) if blocks[i-1] < blocks[i]]
        if thread_count > len(args):
            thread_count = len(args)
        pool = ThreadPool(thread_count)
        pool.map(_worker, args)
        pool.close()
        pool.join()
    if os.path.exists(output):
        os.remove(output)
    os.rename(workpath, output)
    if os.path.exists(infopath):
        os.remove(infopath)
    assert all([block[1] >= block[2] for block in blocks]) is True

def _worker(url, block, fobj, buffer_size):  # 发送请求，确认后开始下载
    req = urllib.request.Request(url)
    req.headers['Range'] = 'bytes=%s-%s' % (block[1], block[2])
    res = urllib.request.urlopen(req)
    while 1:
        chunk = res.read(buffer_size)
        if not chunk:
            break
        with lock:
            fobj.seek(block[1])
            fobj.write(chunk)
            block[1] += len(chunk)

def progress(percent, width=50):  # 显示下载进度
    print("%s %d%%\r" % (('%%-%ds' % width) % (width * percent / 100 ), percent)),
    if percent >= 100:
        print
        sys.stdout.flush()

def write_data(filepath, data):
    with open(filepath, 'wb') as output:
        cPickle.dump(data, output)

def _monitor(infopath, file_info, blocks):
    while 1:
        with lock:
            percent = sum([block[1] - block[0]
                           for block in blocks]) * 100 / file_info.size
            progress(percent)
            if percent >= 100:
                break
            write_data(infopath, (file_info, blocks))
        time.sleep(2)

def read_data(filepath):
    with open(filepath, 'rb') as output:
        return cPickle.load(output)

def getlocalversion(version_path):  # 读取本地版本信息
    f = open(version_path, 'rb')  # 打开路径下的json文件，‘rb’表示文件可读
    data = f.read()
    print(data)
    j = json.loads(data)
    version = j["version"]  # 读取key"version"对应的value值
    print(version)
    return version

def geturl1(version_path, local_url):  # 发送第一条请求将版本信息上传到服务器
    #version_path="/version.json"
    local_version = getlocalversion(version_path)   #将版本号写在http上
    data_content = {'download':'1','version':local_version}
    data_urlencode= urllib.parse.urlencode(data_content)
    print(data_urlencode)
    req = urllib.request.Request(url = local_url, data = data_urlencode.encode(encoding='UTF8'))
    print(req)
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    print(res)
    h = json.loads(res)
    server_version = h["version"]
    print(server_version)
    return server_version  # 服务器返回信息作为返回值

def getYN(res):  # 读取第一条请求的返回信息的YN值    Update=1下载，否则终止下载
    h = json.loads(res)
    YN = h["version"]
    return YN

def getserversion(res):  # 读取第一条请求的返回信息的version值即新版本号
    w = json.loads(res)
    version = w["version"]
    print (version)
    return version


def un_zip(file_name):  # 对下载下来的压缩包进行解压
    zip_file = zipfile.ZipFile(file_name)
    if os.path.isdir(file_name + "_files"):
        pass
    else:
        os.mkdir(file_name + "_files")
    for names in zip_file.namelist():
        zip_file.extract(names, file_name + "_files/")
    zip_file.close()

def delzip(pathT, zipfile_name):  # 删除压缩包
    os.listdir(pathT)
    os.remove(zipfile_name)

def newrename(pathT, j, zipfile_name):  # 将解压后的压缩包更名到  包名+版本号
    os.listdir(pathT)
    b =  '{}{}'.format('rzjh', j) 
    os.rename(zipfile_name + "_files", b.encode("utf-8"))
    return b

def reversion(version_path, new_version):  # 将获取的新版本号替换进老版本信息中
    f = open(version_path, 'r+')
    data = f.read()
    print(data)
    j = json.loads(data)
    print(j)
    #res = geturl1(version_path) 
    j["version"] = new_version
    with open(version_path, 'wb') as f:
        f.write(json.dumps(j).encode("utf-8"))  # 写进json


def rename(pathT,local_version):  # 更改老版本文件名
    os.listdir(pathT)
    b = 'willdele'
    name = '{}{}{}'.format('rzjh', local_version, '.zip')
    if os.path.exists(name):
        os.rename(name, b.encode("utf-8"))
    else:
        pass    

#def delold():  # 删除更名后的老版本
    #shutil.rmtree("将要删除的文件夹路径和文件夹名willdele")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='多线程文件下载器.')
    parser.add_argument('url', type=str, help='下载连接')
    parser.add_argument('-o', type=str, default=None, dest="output", help='输出文件')
    parser.add_argument('-t', type=int, default=defaults['thread_count'], dest="thread_count", help='下载的线程数量')
    parser.add_argument('-b', type=int, default=defaults['buffer_size'], dest="buffer_size", help='缓存大小')
    parser.add_argument('-s', type=int, default=defaults['block_size'], dest="block_size", help='字区大小')
    argv = sys.argv[1:]
    if len(argv) == 0:
        argv = argv = ['http://127.0.0.1/rzjh.zip']
    args = parser.parse_args(argv)
    start_time = time.time()
    pathT = 'rzjh_update'
    version_url = 'http://127.0.0.1/version.json'
    download_url = 'http://127.0.0.1/rzjh.zip'
    version_path = "version.json"
    local_version = getlocalversion(version_path) 
    new_version= geturl1(version_path,version_url )
    # new_version = getserversion(res)
    zipfile_name = '{}{}{}'.format('rzjh', new_version, '.zip')
    if  new_version > local_version:
        print("准备更新，请稍后》》")
        rename(pathT,local_version)
        #download(download_url, output, args.thread_count,
         #        args.buffer_size, args.block_size)
        new_download(download_url,zipfile_name)
        reversion(version_path, new_version)
        #delold()
        un_zip(zipfile_name)
        delzip(pathT, zipfile_name)
        newrename(pathT, new_version, zipfile_name)
    else:
        print ("已经是最新版本《《")
        exit()
