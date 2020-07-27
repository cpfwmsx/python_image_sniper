#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import time


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


if __name__ == '__main__':
    source_path = "http://ww2.sinaimg.cn/bmiddle/9150e4e5gy1gbwe0lxvv6j20280283y9.jpg"
    download_file = "download_%s.jpg" % int(time.time())
    download_http_source(source_path, download_file)


