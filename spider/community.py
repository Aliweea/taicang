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
def add_information(community, address, inform1, inform2, price):
    #read database information form config
    cf = configparser.ConfigParser()
    cf.read("config/spider_community.conf")
    # read by type
    db_table =cf.get("db", "db_table")
    db_community =cf.get("db", "db_community")
    db_address =cf.get("db", "db_address")
    db_inform1 =cf.get("db", "db_inform1")
    db_inform2 =cf.get("db", "db_inform2")
    db_price =cf.get("db", "db_price")
    con, cur = getConnect()

    sql = "INSERT INTO " + db_table + "( "+ db_community+", "\
                                         + db_address + ", "\
                                         + db_inform1 + ","\
                                         + db_inform2 + ","\
                                         + db_price + ") VALUES ({},{},{},{},{})". \
        format(repr(community), repr(address), inform1, inform2, price)

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
    f2 = open('temp/community.txt', 'w', encoding='utf-8')

    for item0 in soup.select('.l'):
        for item in item0.select('dt'):
            try:
                f2.write(item.text)
                # print(item.text)
            except OSError:
                pass
            continue
    f2.close()


def utl():
    with open('temp/community.txt', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        _ = next(csv_reader)  # 读取第一行每一列的标题
        i = 0
        #f2 = open('community2.txt', 'w', encoding='utf-8')
        #f2.write("小区" + ' ' + "地址" + ' ' + "二手房源" + ' ' + "租房房源" + ' ' + "价格" + '\n')
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
            i += 1
            if (i == 3):
                name = str(row)
                # print (name)
                name = name[2:len(name) - 2].strip("'\",")
            if (i == 4):
                location = str(row).split(' ')
                location = location[0].split('：')[1].strip("'\",")

            if (i == 5):
                infor = str(row).split(' ')
                # print (len(infor[0]))
                if (len(infor) > 0):
                    infor1 = infor[0].split('：')

                    if (len(infor1[0]) > 2):
                        # len1 = len(infor1[1])
                        infor1 = infor1[1].strip("套']")
                    else:
                        infor1 = 0

                    if (len(infor) > 1):
                        infor2 = infor[1].split('：')
                        if (len(infor2[0]) > 2):
                            # len2 = len(infor2[1])
                            infor2 = infor2[1].strip("套']")
                        else:
                            infor2 = 0
                else:
                    infor1 = 0
                    infor2 = 0

            if (i == 9):
                price = str(row).split(' ')
                len0 = len(price[0])
                price = price[0][3:len0]
                #f2.write(str(name) + ' ' + str(location) + ' ' + str(infor1) + ' ' + str(infor2) + ' ' + str(price))
                print(str(name) + ' ' + str(location) + ' ' + str(infor1) + ' ' + str(infor2) + ' ' + str(price))
                add_information(str(name),str(location),int(infor1),int(infor2),int(price))

            if (i % 13 == 0):
                i = 0
        # f2.close()


#入口
def community(begin,end):
    cf = configparser.ConfigParser()
    cf.read("config/spider_community.conf")

    str_front=cf.get("web", "front")
    str_after=cf.get("web", "after")

    for i in range(begin,end+1):
        url = str_front+str(i)+str_after
        content(url)
        utl()


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print('请输入起始页数和终止页数')
        exit

    begin = sys.argv[1]
    end = sys.argv[2]
    community(begin, end)