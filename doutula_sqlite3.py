# coding:utf8
import sqlite3
import requests
import re
import time
import logging
import sys

from sqlite3 import DatabaseError
# 示例地址
base_url = "https://www.doutula.com/photo/list/?page=1"
# 带参数的模板地址，本地址为防止错误，使用http，非https
base_url_template = "http://www.doutula.com/photo/list/?page=%d"
# 数据库地址，此处为执行时的路径
file_sqlite3_location = "doutula_images_data.db"


# 创建待解析的地址: 3253
def gen_all_page_url(start_page, total_page):
    page_continue = 0
    print("开始页数：%d，总页数：%d" % (start_page, total_page))
    log_kit_info("开始页数：%d，总页数：%d" % (start_page, total_page))
    for i in range(start_page, total_page + 1):
        url = base_url_template % i
        print("执行地址：%s" % url)
        log_kit_info("解析地址：%s" % url)
        try:
            get_image_list(url)
        except RuntimeError as e:
            log_kit_error("get_image_list运行时错误: %s" % e)
        except Exception as e:
            log_kit_error("get_image_list未意料的错误,程序将重新执行: %s" % e)
            # requests.get("http://192.168.1.20:8000/bee?page=%d" % i, timeout=3)
            page_continue = i
            break
            # sys.exit(0)
        time.sleep(1)
    if page_continue > 0:
        gen_all_page_url(page_continue, total_page)
    else:
        log_kit_info("解析完成，总页数 %d" % total_page)
        # requests.get("http://192.168.1.20:8000/bee?page=%d" % total_page, timeout=3)


# 定义request请求头
def gen_request_headers():
    headers = {
               "accept": "text/html,application/xhtml+xml,application/xml;"
                         "q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "accept-encoding": "gzip, deflate, br",
               "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
               "cookie": "XSRF-TOKEN=eyJpdiI6IjRNWGx5MnhEMTdNUVhacmtSdnE2Mmc9PSIsInZhbHVlIjoiUWVDcDd1SG9Ud3QrdmZKODhPZFRrVW1uRDZCMTA4M0QyZmZaUllvQmtyWkhjQnVvcVhYTjRGYTFWTDNwU2ptNSIsIm1hYyI6Ijk4MWU4NzFhZjJjYmQ4MGU2MDgzZDY1OGU2YTI0MGZjM2Y0OGE5M2ZkYjkzODQzYWRhN2Q4N2M5ZDZjMDYzOTkifQ%3D%3D; doutula_session=eyJpdiI6IkJvZmRHakFcL09Ec1ZlUWNGZVl6d2pnPT0iLCJ2YWx1ZSI6Imk2UVYwQldqT0RBXC9Oemc5R2NyeVBtSktIMGtkOWtqdHFCWFRwZkFaUmFxRk9YbXp4aEEyQlwvcHZuVlM1RFN4XC8iLCJtYWMiOiIwZWNmM2U4MjY4ZWZjODVjZWVhZGVmYzdkYTY2ZDA5ODJiOTQ2MTM0ZmZiMTYyMTA1YjVjZWJjY2ZlNTIwZTUwIn0%3D; Hm_lvt_2fc12699c699441729d4b335ce117f40=1595661921; Hm_lpvt_2fc12699c699441729d4b335ce117f40=1595661921; _agep=1595661921; _agfp=28e31787fe6eec19ff4ab2a7a8aad210; _agtk=7945fc9b3d862ef02d206a327eda802a",
               "dnt": "1",
               "referer": "http://www.doutula.com/photo/list/?page=1",
               "sec-fetch-mode": "navigate",
               "sec-fetch-site": "same-origin",
               "sec-fetch-user": "?1",
               "upgrade-insecure-requests": "1",
               "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
               }
    return headers


# 获取指定页面的所有图片集合，保存到数据库
def get_image_list(request_url):
    try:
        response = requests.get(request_url, timeout=10, headers=gen_request_headers())
        full_doc_str = response.text
        reg = r'data-original="(.*?)".*?alt="(.*?)"'
        reg = re.compile(reg, re.S)
        images_list = re.findall(reg, full_doc_str)
        value_list = []
        exits = False
        # create_tables()
        for image in images_list:
            image_url = image[0]
            image_alt = image[1]
            row_value = (image_url, image_alt, image_url, '8', '0', image_alt)
            exits = exists_data_image(url=image_url)
            if exits is False:
                value_list.append(row_value)
            else:
                # print("数据已存在")
                log_kit_info("数据已存在：%s \n %s" % (request_url, image_url))
        save_image_to_db(value_list)
    except TimeoutError as e:
        print("解析时间超时，程序退出 %s" % e)
        sys.exit(0)


# 获取数据库连接
def get_mysql_connect():
    conn = sqlite3.connect(file_sqlite3_location)
    return conn


def create_tables():
    conn = get_mysql_connect()
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
    # pass


# 保存指定数据集合到数据库
def save_image_to_db(value_list):
    exe_count = 0
    conn = get_mysql_connect()
    conn.text_factory = str  ##!!!
    cursor = conn.cursor()
    # sql_insert = "insert into store_resource_image (image_org_url, image_alt, image_thumb_nail_url,
    # image_category_id, image_state, image_tags) values (%s, %s, %s, %s, %s, %s)"
    sql_insert = "insert into store_resource_image (image_org_url, image_alt, image_thumb_nail_url, " \
                 "image_category_id, image_state, image_tags) values (?,?,?,?,?,?) "
    try:
        exe_count = len(value_list)
        cursor.executemany(sql_insert, value_list)
        conn.commit()
    except DatabaseError as e:
        print("DB产生了异常", e)
        conn.rollback()
    # print("已保存%s条数据" % exe_count)
    log_kit_info("已保存%s条数据" % exe_count)
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


def log_kit_info(msg):
    logging.info(msg=msg)


def log_kit_error(msg):
    logging.error(msg=msg)


# 主函数入口
if __name__ == '__main__':
    logging.basicConfig(filename="logs_doutula.log", filemode="a",
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.INFO)
    # get_image_list(base_url)
    create_tables()
    gen_all_page_url(2285, 3253)
