#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import requests
import time
import os
import shutil
from lxml import html


# 常规下载文件
def download_http_source(source_file_path, output_file):
    try:
        if source_file_path.startswith("http://") or source_file_path.startswith("https://"):
            urllib.request.urlretrieve(source_file_path, output_file)
            return output_file
        else:
            return ""
    except Exception as e:
        print('download_http_source error %s' % str(e))
        return ""


#  批量下载套图
def downloadAlbumWithReferer(title, piclist, referer):
    k = 1
    count = len(piclist)
    dirname = u"[%sP]%s" % (str(count), title)
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    i_header = {}
    i_header['Referer'] = referer
    # 将getPiclink()获取到的妹子的首页网址作为referer字段的值
    for i in piclist:
        filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dirname, k)
        with open(filename, 'wb') as jpg:
            jpg.write(requests.get(i, headers=i_header).content)
            # 将referer字段添加到请求包里并下载图片
            time.sleep(0.5)
        k += 1


if __name__ == '__main__':
    # source_path = "http://ww2.sinaimg.cn/bmiddle/9150e4e5gy1g5zyb6u7h3j205i059q2t.jpg"
    # download_file = "download_%s.jpg" % int(time.time())
    # download_http_source(source_path, download_file)
    print(os.pardir)
    # url = "https://www.mn5.cc/"
    # picList = ["https://www.mn5.cc/uploadfile/202006/29/90213241333.jpg","https://www.mn5.cc/uploadfile/202006/29/41213241655.jpg","https://www.mn5.cc/uploadfile/202006/29/43213241345.jpg"]
    # downloadAlbumWithReferer(title="套图", piclist=picList, referer=url)
