# coding:utf8
import sqlite3
import requests
import re
import time
import logging
import sys

from pyquery import PyQuery as pq
from sqlite3 import DatabaseError


class mzituImage:
    domainUrl = "https://www.mzitu.com/"
    tagUrl = domainUrl + "/tag"
    categoryUrls = ("https://www.mzitu.com/xinggan/", "https://www.mzitu.com/japan/", "https://www.mzitu.com/mm/")

    def __init__(self):
        self.__create_tables()

    def __httpHeader(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "Hm_lvt_cb7f29be3c304cd3bb0c65a4faa96c30=1594272655,1594600625,1595906399; views=3; Hm_lpvt_cb7f29be3c304cd3bb0c65a4faa96c30=1595918526",
            "dnt": "1",
            "referer": "https://www.mzitu.com/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        }
        return headers

    def __getCategoryPages(self, url):
        try:
            doc = pq(url=url, time=10, headers=self.__httpHeader())
            pagination = doc('.pagination a:last-child').prev().text()
            return int(pagination)
        except TimeoutError as e:
            print("解析时间超时，程序退出 %s " % e)
            sys.exit(0)

    def parseCategory(self, categoryUrl, pageNum):
        totalPage = self.__getCategoryPages(categoryUrl)
        print("开始页数: %d, 总页数: %d" % (pageNum, totalPage))
        startUrl = categoryUrl
        if "http" in startUrl:
            imageList = []
            for i in range(pageNum, totalPage + 1):
                parseUrl = startUrl + "page/" + str(i) + "/"
                print(parseUrl)
                doc = pq(url=parseUrl, time=10, headers=self.__httpHeader())
                links = doc("#pins a").items()
                for link in links:
                    img = link.children("img:eq(0)")
                    imgSrc = img.attr("src");
                    thumbSrc = img.attr("data-original");
                    alt = img.attr("alt")
                    if imgSrc is not None:
                        imageDto = (imgSrc, alt, thumbSrc, '8', '0', alt)
                        exists = self.exists_data_image(url=imgSrc)
                        if exists is False:
                            imageList.append(imageDto)
                        else:
                            logging.info(msg="数据已存在")
                    # href = link.attr("href")
                    # print(link.html())
                    time.sleep(1)
            # self.saveImgToDb(imageList=imageList)

    def saveImgToDb(self, imageList):
        exeCount = 0
        conn = self.get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql = "insert into store_resource_image (image_org_url, image_alt, image_thumb_nail_url, " \
              "image_category_id, image_state, image_tags) values (?,?,?,?,?,?) "
        try:
            exeCount = len(imageList)
            cursor.executemany(sql, imageList)
            conn.commit()
        except DatabaseError as e:
            logging.warning(msg="数据库异常")
            conn.rollback()
        finally:
            conn.close()
            logging.info(msg="执行了 %d 条数据" % exeCount)

    # 获取数据库连接
    def get_sqlite_connect(self):
        # 数据库地址，此处为执行时的路径
        file_sqlite3_location = "db/mzitu.db"
        conn = sqlite3.connect(file_sqlite3_location)
        return conn

    def __create_tables(self):
        conn = self.get_sqlite_connect()
        cursor = conn.cursor()
        create_table_script = \
            'CREATE TABLE if not exists ' \
            '"store_resource_image" ("image_id" INTEGER NOT NULL ON CONFLICT ABORT PRIMARY KEY AUTOINCREMENT,' \
            '"image_alt" TEXT(128),"image_tags" TEXT(255),"image_org_url" TEXT(255),' \
            '"image_thumb_nail_url" TEXT(255),"image_category_id" TEXT(20),"image_state" TEXT(3) );'
        cursor.execute(create_table_script)
        create_index_script = \
            'CREATE INDEX if not exists "idx_source_image_org_url" ON "store_resource_image" ("image_org_url" ASC );'
        cursor.execute(create_index_script)

    # 判断指定地址在数据库表中是否已经存在
    def exists_data_image(self, url):
        ets = False
        conn = self.get_sqlite_connect()
        cursor = conn.cursor()
        sql_select = "SELECT image_id \
                    FROM store_resource_image WHERE image_org_url = '%s' limit 1" % url
        cursor.execute(sql_select)
        result = cursor.fetchone()
        if result is not None:
            ets = True
        else:
            ets = False
        conn.close()
        return ets


if __name__ == '__main__':
    mzitu = mzituImage()
    # for categoryUrl in mzitu.categoryUrls:
    #     mzitu.parseCategory(categoryUrl, 1)
    mzitu.parseCategory(mzitu.categoryUrls[2], 1)
