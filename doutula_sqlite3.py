# coding:utf8
import sqlite3
import requests
import re
import time

from sqlite3 import DatabaseError

base_url = "https://www.doutula.com/photo/list/?page=2"
base_url_template = "https://www.doutula.com/photo/list/?page=%d"
file_sqlite3_location = "doutula_images_data.db"


# 创建待解析的地址: 3253
def gen_all_page_url(start_page, total_page):
    print("开始页数：%d，总页数：%d" % (start_page, total_page))
    for i in range(start_page, total_page + 1):
        url = base_url_template % i
        print("执行地址：%s" % url)
        get_image_list(url)
        time.sleep(5)
    pass


# 定义request请求头
def gen_request_headers():
    headers = {":authority": "www.doutula.com",
               ":method": "GET",
               ":path": "/photo/list/?page=3233",
               ":scheme": "https",
               "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "accept-encoding": "gzip, deflate, br",
               "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
               "cookie": "__cfduid=db417b6517eae8505fee3b5849eea23391581148762; UM_distinctid=17023cf8587a0-0bc004f2024266-39647b0e-fa000-17023cf85887ff; _agep=1581148769; _agfp=ebcf2c7646fef9e4419609c2718a976e; _agtk=e56811bdee0b44fc7967997f125be6e1; CNZZDATA1256911977=422772122-1581145937-%7C1581224399; XSRF-TOKEN=eyJpdiI6Ikh6bFg0UmhyajBLeDZxUDhicE1YcUE9PSIsInZhbHVlIjoiWTZzdkFBUWdcL2tSUU96b2RjK1g3UHpvYWRmVnkxb1RaT2Q1alRYME1Bd2JWODVsUjd2cFZSZGlubW5ocWV6OGsiLCJtYWMiOiI2ZGYwNGI0ZDExMjAwZTA3MDhlOTQwZjI4N2U2ZDU0ZDc5YTAyZGFmMjYxOTYxZTRiZDMzYjQ1OTVhYjc5NDhlIn0%3D; doutula_session=eyJpdiI6Imd1TysxV0ZHb3k5M3pTT25sNUMzbHc9PSIsInZhbHVlIjoiT0Z6OXBDbGtyVkpDbHFkOXhtV1ArNFppalZIU0F1aFJjQ2t0NE1VWndQODMyS3ByeUREd1hiaHdQXC9TZnlMSEwiLCJtYWMiOiJiOTdlYTM2OWQxNmUzZTM0OWYxM2UxOTZmY2U3NzAyNDZkYTBlNmJlOTA1NjQ5NWFmZmEwNWJmODk3MTQ3MDYxIn0%3D",
               "dnt": "1",
               "referer": "https://www.doutula.com/photo/list/?page=1",
               "sec-fetch-mode": "navigate",
               "sec-fetch-site": "same-origin",
               "sec-fetch-user": "?1",
               "upgrade-insecure-requests": "1",
               "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
               }
    return headers


# 获取指定页面的所有图片集合，保存到数据库
def get_image_list(request_url):
    response = requests.get(request_url)
    full_doc_str = response.text
    reg = r'data-original="(.*?)".*?alt="(.*?)"'
    reg = re.compile(reg, re.S)
    images_list = re.findall(reg, full_doc_str)
    value_list = []
    exits = False
    create_tables()
    for image in images_list:
        image_url = image[0]
        image_alt = image[1]
        row_value = (image_url, image_alt, image_url, '8', '0', image_alt)
        exits = exists_data_image(url=image_url)
        if exits is False:
            value_list.append(row_value)
        else:
            print("数据已存在")
    save_image_to_db(value_list)


# 获取数据库连接
def get_mysql_connect():
    conn = sqlite3.connect(file_sqlite3_location)
    return conn


def create_tables():
    # conn = get_mysql_connect()
    # cursor = conn.cursor()
    # create_table_script = 'CREATE TABLE if not exists "store_resource_image" ("image_id" INTEGER NOT NULL ON CONFLICT ABORT PRIMARY KEY AUTOINCREMENT,"image_alt" TEXT(128),"image_tags" TEXT(255),"image_org_url" TEXT(255),"image_thumb_nail_url" TEXT(255),"image_category_id" TEXT(20),"image_state" TEXT(3) );'
    # cursor.execute(create_table_script)
    # create_index_script = 'CREATE INDEX if not exists "idx_source_image_org_url" ON "store_resource_image" ("image_org_url" ASC );'
    # cursor.execute(create_index_script)
    pass


# 保存指定数据集合到数据库
def save_image_to_db(value_list):
    exe_count = 0
    conn = get_mysql_connect()
    conn.text_factory = str  ##!!!
    cursor = conn.cursor()
    # sql_insert = "insert into store_resource_image (image_org_url, image_alt, image_thumb_nail_url, image_category_id, image_state, image_tags) values (%s, %s, %s, %s, %s, %s)"
    sql_insert = "insert into store_resource_image (image_org_url, image_alt, image_thumb_nail_url, image_category_id, image_state, image_tags) values (?,?,?,?,?,?)"
    try:
        exe_count = len(value_list)
        cursor.executemany(sql_insert, value_list)
        conn.commit()
    except RuntimeError as e:
        print("操作产生了异常", e)
        conn.rollback()
    except DatabaseError as e:
        print("DB产生了异常", e)
        conn.rollback()
    print("已保存%s条数据" % exe_count)
    conn.close()


# 判断指定地址在数据库表中是否已经存在
def exists_data_image(url):
    ets = False
    conn = get_mysql_connect()
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


# 主函数入口
if __name__ == '__main__':
    # get_image_list(base_url)
    gen_all_page_url(1, 3253)
