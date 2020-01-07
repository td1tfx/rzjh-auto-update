import sys
import requests
import os
import urllib
import json
import zipfile
import time
import shutil


def newDownload(url, file_path, ui):
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
                done_2 = int(100 * temp_size / total_size)
                done_3 = 0
                if done_2 % 10 == 0 and done_2 > done_3:
                   done_3 = done_2
                   ui.printf("已完成:"+str(done_2))
    print()  # 避免上面\r 回车符

def getLocalVersion(version_path):  # 读取本地版本信息
    f = open(version_path, 'rb')  # 打开路径下的json文件，‘rb’表示文件可读
    data = f.read()
    #print(data)
    j = json.loads(data)
    version = j["version"]  # 读取key"version"对应的value值
    return version

def getServerIp(version_path):  # 读取本地版本信息
    f = open(version_path, 'rb')  # 打开路径下的json文件，‘rb’表示文件可读
    data = f.read()
    #print(data)
    j = json.loads(data)
    serverip = j["serverip"]  # 读取key"version"对应的value值
    return serverip

def geturl1(local_version, local_url):  # 发送第一条请求将版本信息上传到服务器
    data_content = {'download':'1','version':local_version}
    data_urlencode= urllib.parse.urlencode(data_content)
    #print(data_urlencode)
    req = urllib.request.Request(url = local_url, data = data_urlencode.encode(encoding='UTF8'), method='GET')
    try:
        res_data = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.reason)
        return -1
    except urllib.error.URLError as e:
        # print(e.code)
        print(e.reason)
        return -1
    res = res_data.read()
    h = json.loads(res)
    server_version = h["version"]
    return server_version  # 服务器返回信息作为返回值



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

def newRename(pathT, j, zipfile_name):  # 将解压后的压缩包更名到  包名+版本号
    os.listdir(pathT)
    b =  '{}{}'.format('rzjh_patch', j)
    if os.path.exists(b):
        shutil.rmtree(b)
        os.rename(zipfile_name + "_files", b.encode("utf-8"))
    else:
        os.rename(zipfile_name + "_files", b.encode("utf-8"))
    return b

def reversion(version_path, new_version):  # 将获取的新版本号替换进老版本信息中
    f = open(version_path, 'r+')
    data = f.read()
    #print(data)
    j = json.loads(data)
    #print(j)
    #res = geturl1(version_path) 
    j["version"] = new_version
    with open(version_path, 'wb') as f:
        f.write(json.dumps(j).encode("utf-8"))  # 写进json


def rename(pathT,local_version):  # 更改老版本文件名
    if os.path.exists(pathT):
        pass
    else:
        os.mkdir(pathT)
    os.listdir(pathT)
    b = 'willdele'
    name = '{}{}{}'.format('rzjh', local_version, '.zip')
    if os.path.exists(name):
        os.rename(name, b.encode("utf-8"))
    else:
        pass    

#def delold():  # 删除更名后的老版本
    #shutil.rmtree("将要删除的文件夹路径和文件夹名willdele")

def moveTree(path_s, path_d):
    files = os.listdir(path_s)
    for file in files:
        path_file = path_s + "\\" + file
        dest_file = path_d + "\\" + file
        if os.path.isfile(dest_file):
            if os.path.exists(dest_file):
                os.remove(dest_file)
                shutil.move(path_file, path_d)
            else:
                shutil.move(path_file, path_d)
        else:
            moveTree(path_file, dest_file)




def doUpdate(ui):
    version_path = "config.json"
    server_ip = getServerIp(version_path)
    ui.printf("连接更新服务器：" + str(server_ip))
    version_url = '{}{}{}'.format('http://', server_ip, '/version.json')
    download_url = '{}{}{}'.format('http://', server_ip, '/rzjh.zip')
    gxtxt_url = '{}{}{}'.format('http://', server_ip, '/gx.txt')
    local_version = getLocalVersion(version_path)
    ui.printf("本地版本：" + str(local_version))
    new_version= geturl1(local_version,version_url)
    ui.printf("服务器版本：" + str(new_version))
    pathT = 'rzjh_update'
    ui.printf("准备更新，请稍后》》")
    local_version = getLocalVersion(version_path)
    rename(pathT, local_version)
    zipfile_name = '{}{}{}'.format('rzjh', new_version, '.zip')
    gxtxt_name = 'rzjh_gx.txt'
    newDownload(gxtxt_url, gxtxt_name, ui)
    newDownload(download_url, zipfile_name, ui)
    ui.printf("下载完毕》》")
    ui.printf("正在解压，请稍后》》")
    reversion(version_path, new_version)
    un_zip(zipfile_name)
    delzip(pathT, zipfile_name)
    new_name = newRename(pathT, new_version, zipfile_name)
    ui.printf("正在执行文件替换，请稍后》》")
    moveTree(new_name, ".\\")
    ui.printf("文件替换完成，启动游戏》》")



def checkUpdate(ui):
    start_time = time.time()
    version_path = "config.json"
    server_ip = getServerIp(version_path)
    ui.printf("连接更新服务器：" + str(server_ip))
    version_url = '{}{}{}'.format('http://', server_ip, '/version.json')
    download_url = '{}{}{}'.format('http://', server_ip, '/rzjh.zip')
    local_version = getLocalVersion(version_path)
    ui.printf("本地版本：" + str(local_version))
    new_version= geturl1(local_version,version_url )
    if new_version <= 0:
        ui.printf("当前服务器繁忙,请稍后再试》》")
        return -1
    ui.printf("服务器版本：" + str(new_version))
    if  new_version > local_version:
        ui.printf("有可用更新》》")
        return 1
    else:
        ui.printf("已经是最新版本《《")
        return 0

