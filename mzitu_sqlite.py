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

    # 定义请求头，模拟浏览器
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

    # 获取分类的总页数
    def __getCategoryPages(self, url):
        try:
            doc = pq(url=url, time=10, headers=self.__httpHeader())
            pagination = doc('.pagination a:last-child').prev().text()
            return int(pagination)
        except TimeoutError as e:
            print("解析时间超时，程序退出 %s " % e)
            sys.exit(0)

    # 获取相册内图片页数
    def __getAlbumImagePages(self, url):
        try:
            doc = pq(url=url, time=10, headers=self.__httpHeader())
            pagination = doc('.pagenavi a:last-child').prev().text()
            return int(pagination)
        except TimeoutError as e:
            print("解析时间超时，程序退出 %s " % e)
            sys.exit(0)

    # 抓取分类数据保存到相册
    def parseCategory(self, categoryUrl, pageNum):
        totalPage = self.__getCategoryPages(categoryUrl)
        print("开始页数: %d, 总页数: %d" % (pageNum, totalPage))
        startUrl = categoryUrl
        if "http" in startUrl:
            for i in range(pageNum, totalPage + 1):
                parseUrl = startUrl + "page/" + str(i) + "/"
                print(parseUrl)
                doc = pq(url=parseUrl, time=10, headers=self.__httpHeader())
                links = doc("#pins a").items()
                albumList = []
                for link in links:
                    img = link.children("img:eq(0)")
                    imgSrc = img.attr("src");
                    thumbSrc = img.attr("data-original");
                    alt = img.attr("alt")
                    href = link.attr("href")
                    updateDate = link.parent().children("span.time").text();
                    if imgSrc is not None:
                        albumDto = (alt, href, thumbSrc, updateDate)
                        exists = self.exists_data_album(url=imgSrc)
                        if exists is False:
                            albumList.append(albumDto)
                        else:
                            logging.info(msg="数据已存在")
                    time.sleep(1)
                self.__saveAlbumToDb(albumList=albumList)

    # 保存相册到数据库
    def __saveAlbumToDb(self, albumList):
        logging.info(msg="本次批量插入相册行数:" + str(albumList.__sizeof__()))
        exeCount = 0
        conn = self.get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql = "insert into store_resource_album (album_title, org_url, cover_image, update_date) values (?,?,?,?) "
        try:
            exeCount = len(albumList)
            cursor.executemany(sql, albumList)
            conn.commit()
        except DatabaseError as e:
            logging.warning(msg="数据库异常")
            conn.rollback()
        finally:
            conn.close()
            logging.info(msg="执行了 %d 条数据" % exeCount)

    # 解析相册，保存相册图片
    def parseImageByAlbum(self, pageSize):
        dataList = self.__findAlbumByDataState(0, pageSize)
        if dataList is None:
            print("finish now")
        else:
            for data in dataList:
                albumId = data[0]
                albumUrl = data[2]
                self.__parseImageByAlbumId(albumId=albumId, albumUrl=albumUrl)

    # 根据相册和相册原始地址解析图片保存到相册
    def __parseImageByAlbumId(self, albumId, albumUrl):
        totalPage = self.__getAlbumImagePages(albumUrl)
        for i in range(1, totalPage + 1):
            url = ''
            if i == 1:
                url = albumUrl
            else:
                url = albumUrl + "/" + str(i)
            self.__saveImageByAlbumAndUrl(albumId=albumId, docUrl=url)

    # 指定相册id和图片dom单条保存图片
    def __saveImageByAlbumAndUrl(self, albumId, docUrl):
        doc = pq(url=docUrl, time=10, headers=self.__httpHeader())
        imageDom = doc('.main-image>p>a>img').eq(0)
        src = imageDom.attr("src")
        alt = imageDom.attr("alt")
        if src is None or alt is None:
            print("图片获取失败：" + docUrl)
            return
        else:
            imgDto = (albumId, src, alt, src, 8, 1, alt)
            exists = self.exists_data_image(url=src)
            if exists is False:
                self.__saveImgToDb(imgDto)
                print("指定图片已保存:" + src)
            else:
                print("图片已存在，忽略")

    # 根据数据状态查询指定数量的相册集合
    def __findAlbumByDataState(self, dataState, pageSize):
        conn = self.get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql_select = "SELECT * from store_resource_album WHERE data_state = " + str(dataState)
        cursor.execute(sql_select)
        result = cursor.fetchmany(pageSize)
        if result is not None:
            return result;
        else:
            print("there is no more data in album")
            return None;

    # 保存图片到数据库
    def __saveImgToDb(self, imageDto):
        exeCount = 0
        conn = self.get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql = "insert into store_resource_image (album_id, image_org_url, image_alt, image_thumb_nail_url, " \
              "image_category_id, image_state, image_tags) values (?,?,?,?,?,?,?) "
        try:
            exeCount = 1
            cursor.execute(sql, imageDto)
            conn.commit()
        except DatabaseError as e:
            logging.warning(msg="数据库异常")
            conn.rollback()
        finally:
            conn.close()
            logging.info(msg="执行了 %d 条数据" % exeCount)

    # 批量保存图片到数据库
    def __saveImgToDbWithList(self, imageList):
        logging.info(msg="本次批量插入图片行数:" + str(imageList.__sizeof__()))
        exeCount = 0
        conn = self.get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql = "insert into store_resource_image (album_id, image_org_url, image_alt, image_thumb_nail_url, " \
              "image_category_id, image_state, image_tags) values (?,?,?,?,?,?,?) "
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

    # 更新相册数据状态
    def __updateAlbumDataState(self, albumId, dataState):
        conn = self.get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql = "UPDATE store_resource_album set data_state = ? where album_id =	?"
        try:
            cursor.execute(sql, dataState, albumId)
            conn.commit()
        except DatabaseError as e:
            logging.warning(msg="数据库异常")
            conn.rollback()
        finally:
            conn.close()

    # 获取数据库连接
    def get_sqlite_connect(self):
        # 数据库地址，此处为执行时的路径
        file_sqlite3_location = "db/mzitu.db"
        conn = sqlite3.connect(file_sqlite3_location)
        return conn

    # 创建所需的数据库表
    def __create_tables(self):
        conn = self.get_sqlite_connect()
        cursor = conn.cursor()
        create_table_script = \
            '  CREATE TABLE if not exists "store_resource_album" (' \
            '  "album_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' \
            '  "album_title" TEXT NOT NULL,' \
            '  "org_url" TEXT,' \
            '  "cover_image" TEXT,' \
            '  "update_date" TEXT,' \
            '   "data_state" INTEGER DEFAULT 0) '
        cursor.execute(create_table_script)
        create_index_script = 'CREATE UNIQUE INDEX if not exists "idx_resource_album_org_id"' \
                              ' ON "store_resource_album" ("org_url");'
        cursor.execute(create_index_script)
        create_table_script = \
            'CREATE TABLE if not exists ' \
            '"store_resource_image" ("image_id" INTEGER NOT NULL ON CONFLICT ABORT PRIMARY KEY AUTOINCREMENT,' \
            '"album_id" INTEGER NOT NULL DEFAULT 0,'\
            '"image_alt" TEXT(128),"image_tags" TEXT(255),"image_org_url" TEXT(255),' \
            '"image_thumb_nail_url" TEXT(255),"image_category_id" TEXT(20),"image_state" TEXT(3) );'
        cursor.execute(create_table_script)
        create_index_script = \
            'CREATE INDEX if not exists "idx_source_image_org_url" ON "store_resource_image" ("image_org_url" ASC );'
        cursor.execute(create_index_script)
        create_index_script = \
            'CREATE INDEX if not exists "idx_source_image_album_id" ON "store_resource_image" ("album_id" ASC );'
        cursor.execute(create_index_script)

    # 判断指定地址在相册表中是否已经存在
    def exists_data_album(self, url):
        ets = False
        conn = self.get_sqlite_connect()
        cursor = conn.cursor()
        sql_select = "SELECT album_id \
                    FROM store_resource_album WHERE org_url = '%s' limit 1" % url
        cursor.execute(sql_select)
        result = cursor.fetchone()
        if result is not None:
            ets = True
        else:
            ets = False
        conn.close()
        return ets


    # 判断指定地址在图片表中是否已经存在
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
    # mzitu.parseCategory(mzitu.categoryUrls[0], 1)
    mzitu.parseImageByAlbum(pageSize=1)