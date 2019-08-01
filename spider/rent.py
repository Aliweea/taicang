import re
from lxml import html
import xml
import requests
from bs4 import BeautifulSoup
import csv
import configparser
import os
import sys

cur_dir = os.path.abspath(os.path.dirname(__file__))
pro_dir = os.path.split(cur_dir)[0]
sys.path.append(pro_dir)

from db.database import getConnect

# insert
def add_information(community, address, layout, build_time, height, toward, price):
    cf = configparser.ConfigParser()
    cf.read("config/spider_rent.conf")
    db_table =cf.get("db", "db_table")
    db_community =cf.get("db", "db_community")
    db_address =cf.get("db", "db_address")
    db_layout =cf.get("db", "db_layout")
    db_build_time =cf.get("db", "db_build_time")
    db_height =cf.get("db", "db_height")
    db_toward =cf.get("db", "db_toward")
    db_price =cf.get("db", "db_price")

    con, cur = getConnect()

    sql = "INSERT INTO " + db_table + "( "+ db_community + ", "\
                                        + db_address + ", "\
                                        + db_layout + ", "\
                                        + db_build_time + ", "\
                                        + db_height + ", "\
                                        + db_toward + ", "\
                                        + db_price + ") VALUES ({},{},{},{},{},{},{})". \
        format(repr(community), repr(address), repr(layout), build_time, repr(height), repr(toward), price)

    try:
        cur.execute(sql)
        con.commit()
    except Exception as e:
        con.rollback()
        print(e)

    cur.close()
    con.close()


def content(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html5lib")
    #f2 = open('市区.txt','a+',encoding='utf-8')

    for item0 in soup.select('.house'):
        for item in item0.select('li'):
            try:
                if (len(item.select("dd")) > 4):
                    location=item.select("dd")[0].text.split('\xa0', 2)
                    # le=len(location)
                    inform = item.select("dd")[1].text
                else:
                    location = item.select("div")[0].text.split('\xa0', 2)
                    inform = item.select("dd")[0].text

                community = location[0]
                address = location[len(location)-1]
                price = item.select("dt")[1].text.strip("元/月")
                infos = inform.split('|')
                layout = infos[0].strip()
                build_time = infos[1].strip(" 年建造")
                height = infos[2]
                toward = infos[3]
                print(community + ' ' + address + ' ' + layout + ' ' + build_time + ' ' + height + ' ' + toward + ' ' + price + '\n')
                add_information(community, address, layout, build_time, height, toward, price)

            except OSError:
                pass
            continue
    #f2.close()


#租房爬虫入口（爬虫起始页，截止页）
def rent(begin, end):
    cf = configparser.ConfigParser()
    cf.read("config/spider_rent.conf")

    str_front = cf.get("web", "front")
    str_after = cf.get("web", "after")
    
    for i in range(begin,end+1):
        url = str_front + str(i) + str_after
        #print(url)
        content(url)

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print('请输入起始页数和终止页数')
        exit

    begin = sys.argv[1]
    end = sys.argv[2]
    rent(begin, end)