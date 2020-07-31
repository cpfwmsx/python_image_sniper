# coding:utf8
# -*- coding:utf-8 -*-
import sqlite3
import requests
import re
import time
import logging
import sys

from pyquery import PyQuery as pq
from sqlite3 import DatabaseError


# 美女屋图片抓取
class mn5Image:
    domainUrl = "https://www.mn5.cc"
    tagUrl = domainUrl + "/tag"
    categoryUrls = (
    "https://www.mn5.cc/Xgyw/", "https://www.mn5.cc/Tuigirl/", "https://www.mn5.cc/Ugirls/", "https://www.mn5.cc/Tgod/",
    "https://www.mn5.cc/TouTiao/",
    "https://www.mn5.cc/Girlt/", "https://www.mn5.cc/Aiyouwu/", "https://www.mn5.cc/LEGBABY/",
    "https://www.mn5.cc/Mtcos/", "https://www.mn5.cc/MissLeg/",
    "https://www.mn5.cc/BoLoli/", "https://www.mn5.cc/Slady/", "https://www.mn5.cc/YouMei/",
    "https://www.mn5.cc/Xiuren/", "https://www.mn5.cc/MyGirl/",
    "https://www.mn5.cc/YouWu/", "https://www.mn5.cc/IMiss/", "https://www.mn5.cc/MiiTao/", "https://www.mn5.cc/Uxing/",
    "https://www.mn5.cc/FeiLin/",
    "https://www.mn5.cc/MiStar/", "https://www.mn5.cc/Tukmo/", "https://www.mn5.cc/WingS/",
    "https://www.mn5.cc/LeYuan/", "https://www.mn5.cc/Taste/",
    "https://www.mn5.cc/MFStar/", "https://www.mn5.cc/Huayan/", "https://www.mn5.cc/DKGirl/",
    "https://www.mn5.cc/Candy/", "https://www.mn5.cc/YouMi/",
    "https://www.mn5.cc/MintYe/", "https://www.mn5.cc/Micat/", "https://www.mn5.cc/Mtmeng/",
    "https://www.mn5.cc/HuaYang/", "https://www.mn5.cc/XingYan/",
    "https://www.mn5.cc/XiaoYu/")

    def __init__(self):
        self.__createTables()

    # 设置请求头
    def __httpHeader(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "UM_distinctid=1739936376ab5-0be5a578c7bdd7-b7a1334-1fa400-1739936376b499; CNZZDATA1263487746=1772237929-1596000738-https%253A%252F%252Fwww.mn5.cc%252F%7C1596000738; __51cke__=; __tins__19410367=%7B%22sid%22%3A%201596003334000%2C%20%22vd%22%3A%205%2C%20%22expires%22%3A%201596006017846%7D; __51laig__=5",
            "DNT": "1",
            "Host": "www.mn5.cc",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        }
        return headers

    # 获取分类最大页码
    def __getCategoryPages(self, url):
        try:
            doc = pq(url=url, time=10, headers=self.__httpHeader(), encoding="gbk")
            pagefullDoc = doc('.page').eq(0)
            pagefullDoc.remove("span")
            totalSize = pagefullDoc.find("a").length
            totalPageLink = pagefullDoc.find("a").eq(totalSize - 1)
            href = totalPageLink.attr("href");
            reg = r'page_(.*?).html'
            reg = re.compile(reg, re.S)
            pageCount = re.findall(reg, href)
            if len(pageCount) > 0:
                return int(pageCount[0])
            else:
                return 1
        except TimeoutError as e:
            print("解析时间超时，程序退出 %s " % e)
            sys.exit(0)

    # 根据分类地址和开始页码抓取数据
    def parseCategory(self, categoryUrl, pageNum):
        totalPage = self.__getCategoryPages(categoryUrl)
        print("开始页数: %d, 总页数: %d" % (pageNum, totalPage))
        startUrl = categoryUrl
        if "http" in startUrl:
            albumList = []
            for i in range(pageNum, totalPage + 1):
                parseUrl = startUrl
                if i != 1:
                    parseUrl = startUrl + "page_" + str(i) + ".html"
                print("parseUrl %s" % parseUrl)
                doc = pq(url=parseUrl, time=10, headers=self.__httpHeader(), encoding="gbk")
                bianks = doc(".biank1").items()
                for biank in bianks:
                    link = biank.find("a:first-child")
                    imagesUrl = link.attr("href");
                    orgSourceAlbumUrl = self.domainUrl + imagesUrl
                    existsAlbum = self.__existsDataAlbum(orgSourceAlbumUrl)
                    if existsAlbum is False:
                        img = biank.find("img:first-child");
                        imgSrc = img.attr("src");
                        thumbSrc = imgSrc;
                        albumName = img.attr("title")
                        albumDesc = albumName
                        categoryId = 9
                        albumCoverMap = self.domainUrl + imgSrc
                        albumTags = albumName
                        albumSort = 1
                        albumState = 0
                        album = (
                        albumName, albumCoverMap, albumDesc, categoryId, orgSourceAlbumUrl, albumTags, albumSort,
                        albumState)
                        albumList.append(album)
                    else:
                        print("指定相册已经存在 %s" % orgSourceAlbumUrl)
                time.sleep(1)
            self.__saveAlbumToDb(albumList)

    # 获取相册最大页码
    def __getAlbumImagePages(self, url):
        try:
            doc = pq(url=url, time=10, headers=self.__httpHeader(), encoding="gbk")
            pagefullDoc = doc('.page').eq(0)
            totalSize = pagefullDoc.find("a").length
            totalPageLink = pagefullDoc.find("a").eq(totalSize - 2)
            pageCount = totalPageLink.text()
            if len(pageCount) > 0:
                return int(pageCount)
            else:
                return 1
        except TimeoutError as e:
            print("解析时间超时，程序退出 %s " % e)
            sys.exit(0)

    # 根据相册分析相册图片详细
    def parseAlbumImagesByDb(self, albumId):
        albumList = []
        if albumId is None or albumId <= 0:
            print("未传入相册Id，开始爬取所有")
            albumList = self.__selectAlbumByState(albumId=0, albumState=0, start=0, limit=1)
        else:
            print(("爬取指定相册id %d") % albumId)
            albumList = self.__selectAlbumByState(albumId=albumId, albumState=0, start=0, limit=5)
        if len(albumList) == 0:
            print("相册暂无未处理的数据 albumState = %d" % 0)
        for album in albumList:
            albumId = album[0]
            albumOrgUrl = album[5]
            totalPage = self.__getAlbumImagePages(albumOrgUrl)
            startParseUrl = albumOrgUrl
            for i in range(1, totalPage + 1):
                if i > 1:
                    startParseUrl = albumOrgUrl.replace(".html", "") + "_" + str(i) + ".html"
                print("startParseUrl %s" % startParseUrl)
                doc = pq(url=startParseUrl, time=10, headers=self.__httpHeader(), encoding="gbk")
                imageDomList = doc.find(".img>p>img").items()
                imageList = []
                for imageDom in imageDomList:
                    imageAlt = imageDom.attr("alt")
                    imageTags = imageAlt
                    imageOrgUrl = self.domainUrl + imageDom.attr("src")
                    imageThumbNailUrl = imageOrgUrl
                    imageCategoryId = 9
                    imageState = 0
                    exists = self.__existsDataImageAlbum(albumId=albumId, url=imageOrgUrl)
                    if exists is False:
                        imageDto = (
                        albumId, imageAlt, imageTags, imageOrgUrl, imageThumbNailUrl, imageCategoryId, imageState)
                        imageList.append(imageDto)
                    else:
                        print("exists image like %s" % imageOrgUrl)
                if len(imageList) > 0:
                    self.__saveImgToDb(imageList)
                time.sleep(1)
            self.__updateAlbumStateByAlbumId(albumId=albumId, albumState=1)

    # 根据相册状态查询集合
    def __selectAlbumByState(self, albumId, albumState, start, limit):
        albumList = []
        conn = self.__get_sqlite_connect()
        try:
            # conn.text_factory = str ##!!!
            cursor = conn.cursor()
            sql = ''
            if albumId > 0:
                sql = "select * from store_resource_album where album_id = %d and album_state = %d limit %d, %d" % (
                albumId, albumState, start, limit)
            else:
                sql = "select * from store_resource_album where album_state = %d limit %d, %d" % (
                albumState, start, limit)
            # print("sql = %s" % sql)
            cursorResult = cursor.execute(sql)
            for row in cursorResult:
                albumList.append(row)
            return albumList
        except DatabaseError as e:
            logging.warning(msg="数据库异常")
            conn.rollback()
        finally:
            conn.close()
        return albumList

    # 将相册保存到数据库表
    def __saveAlbumToDb(self, albumList):
        exeCount = 0
        conn = self.__get_sqlite_connect()
        try:
            conn.text_factory = str  ##!!!
            cursor = conn.cursor()
            sql = "INSERT INTO store_resource_album ( album_name, album_cover_map, album_desc, category_id, org_source_alubm_url, album_tags, album_sort, album_state )" \
                  " VALUES ( ?, ?, ?, ?, ?, ?, ?, ?);"
            exeCount = len(albumList)
            cursor.executemany(sql, albumList)
            conn.commit()
        except DatabaseError as e:
            logging.warning(msg="数据库异常")
            conn.rollback()
        finally:
            conn.close()
            logging.info(msg="执行了 %d 条数据" % exeCount)

    # 将图片保存到数据库表
    def __saveImgToDb(self, imageList):
        exeCount = 0
        conn = self.__get_sqlite_connect()
        conn.text_factory = str  ##!!!
        cursor = conn.cursor()
        sql = "INSERT INTO store_resource_image ( album_id, image_alt, image_tags, image_org_url, image_thumb_nail_url, image_category_id, image_state ) VALUES (?,?,?,?,?,?,?);"
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

    # 根据相册id更新相册状态
    def __updateAlbumStateByAlbumId(self, albumId, albumState):
        conn = self.__get_sqlite_connect()
        try:
            cursor = conn.cursor()
            sql = "update store_resource_album set album_state = %d where album_state = %d" % (albumState, albumId)
            cursor.execute(sql)
            conn.commit()
        except DatabaseError as e:
            print(e)
        finally:
            conn.close()

    # 获取数据库连接
    def __get_sqlite_connect(self):
        # 数据库地址，此处为执行时的路径
        file_sqlite3_location = "db/mn5.db"
        conn = sqlite3.connect(file_sqlite3_location)
        return conn

    # 创建必要的数据库表
    def __createTables(self):
        conn = self.__get_sqlite_connect()
        try:
            cursor = conn.cursor()
            create_table_script = \
                'CREATE TABLE if not exists ' \
                '"store_resource_image" ("image_id" INTEGER NOT NULL ON CONFLICT ABORT PRIMARY KEY AUTOINCREMENT,' \
                '"album_id" INTEGER, "image_alt" TEXT(128),"image_tags" TEXT(255),"image_org_url" TEXT(255),' \
                '"image_thumb_nail_url" TEXT(255),"image_category_id" TEXT(20),"image_state" TEXT(3) );'
            cursor.execute(create_table_script)
            create_index_script = \
                'CREATE INDEX if not exists "idx_source_image_org_url" ON "store_resource_image" ("image_org_url" ASC );'
            cursor.execute(create_index_script)
            create_table_script = 'CREATE TABLE if not exists  "store_resource_album" ' \
                                  '( "album_id" INTEGER NOT NULL ON CONFLICT ABORT PRIMARY KEY AUTOINCREMENT, ' \
                                  '"album_name" TEXT(255), "album_cover_map" TEXT(255), "album_desc" TEXT(255) , "category_id" INTEGER NOT NULL, ' \
                                  '"org_source_alubm_url" TEXT(255) , "album_tags" TEXT(255) , "album_sort" INTEGER NOT NULL, "album_state" INTEGER NOT NULL );'
            cursor.execute(create_table_script)
            create_index_script = 'CREATE INDEX if not exists "idx_source_album_org_source_alubm_url" ON "store_resource_album" ("org_source_alubm_url" ASC );'
            cursor.execute(create_index_script)
            create_index_script = 'CREATE INDEX if not exists "idx_resource_image_album_image_url" ON "store_resource_image" ("album_id", "image_org_url");'
            cursor.execute(create_index_script)
            conn.commit()
        except DatabaseError as e:
            print(e)
        finally:
            conn.close()

    # 判断指定相册是否已经存在
    def __existsDataAlbum(self, url):
        exists = False
        conn = self.__get_sqlite_connect()
        cursor = conn.cursor()
        sql = "select album_id from store_resource_album where org_source_alubm_url = '%s' limit 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is not None:
            exists = True
        else:
            exists = False
        conn.close()
        return exists;

    # 判断指定地址在数据库表中是否已经存在
    def __existsDataImage(self, url):
        ets = False
        conn = self.__get_sqlite_connect()
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

    # 判断指定地址和相册id在数据库表中是否已经存在
    def __existsDataImageAlbum(self, url, albumId):
        ets = False
        conn = self.__get_sqlite_connect()
        cursor = conn.cursor()
        sql_select = "SELECT image_id \
                    FROM store_resource_image WHERE album_id = %d and image_org_url = '%s' limit 1" % (albumId, url)
        cursor.execute(sql_select)
        result = cursor.fetchone()
        if result is not None:
            ets = True
        else:
            ets = False
        conn.close()
        return ets


# 文件执行入口
if __name__ == '__main__':
    mn5 = mn5Image()
    # 循环抓取所有分类的相册，并将相册保存到数据库中
    # for categoryUrl in mn5.categoryUrls:
    #     mn5.parseCategory(categoryUrl=categoryUrl, pageNum=1)

    # 只抓取指定第0个分类的相册，并将相册保存到数据库中
    mn5.parseCategory(categoryUrl = mn5.categoryUrls[0], pageNum = 1)

    # 根据数据库中的相册，抓取所属相册的图片入库
    # mn5.parseAlbumImagesByDb(albumId=101)
