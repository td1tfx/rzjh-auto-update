import sys
import requests
import os


#
requests.packages.urllib3.disable_warnings()

def downloadfile(url, file_path):
    r1=requests.get(url, stream=True, verify=False)
    total_size=int(r1.hearders["content-length"])
    if(os.path.exists(file_path)):
        temp_size=os.path.getsize(file_path)
    else:
        temp_size=0;
    print(temp_size, total_size)
    # 断点续传
    hearders={'Range':'bytes=%d-'%temp_size}
    r=requests.get(url,stream=True,verify=False,headers=headers)

    with open(file_path, 'ab+') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s]%d%%" % ('*' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()


def getlocalversion(versionpath):  # 读取本地版本信息
    f = open(versionpath, 'rb')  # 打开路径下的json文件，‘rb’表示文件可读
    data = f.read()
    print data
    j = json.loads(data)
    version = j["version"]  # 读取key"version"对应的value值
    print version
    return version

def geturl1(pack_path):  # 发送第一条请求将版本信息上传到服务器
    url = pack_path + getlocalversion(versionpath)   #将版本号写在http上
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res  # 服务器返回信息作为返回值

def getYN(res):  # 读取第一条请求的返回信息的YN值    Update=1下载，否则终止下载
    h = json.loads(res)
    YN = h["Update"]
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
    b = 'filename' + j
    os.rename(zipfile_name + "_files", b.encode("utf-8"))
    return b

def reversion(jsonpath):  # 将获取的新版本号替换进老版本信息中
    f = open(jsonpath, 'r+')
    data = f.read()
    print data
    j = json.loads(data)
    j["version"] = getserversion()
    with open(jsonpath, 'wb') as f:
        f.write(json.dumps(j))  # 写进json

if __name__=='__main__':
    link=r'http://130.34.192.71'
    UUID=r'update.zip'
    pack_path="rzjh/my.zip"
    ver_path="rzjh/version.json"
    version=getlocalversion(ver_path)
    url=os.path.join(link,UUID)
    downloadfile(url,path)
