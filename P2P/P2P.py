import urllib.request
import pymysql
from lxml import etree
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email import encoders
from email.header import Header
import smtplib
import time
import sys
import traceback
import re
import json
import threading
from enum import Enum
from selenium import webdriver
from bs4 import BeautifulSoup
from mysql_config import *

class mysqlClient:
    def __init__(self, host, port, user, password, db):
        self.pyClient = pymysql.connect(host = host, port = port, user = user, password = password, database = db, charset='utf8')

    def query(self, sql, strTitle):
        cursor = self.pyClient.cursor()
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                if strTitle == row[0]:
                    return True
        except Exception:
            print(Exception)
            traceback.print_exc()
            print('exec sql fail:',sql)
        return False

    def insertOrUpdateGood(self, sql):
        cursor = self.pyClient.cursor()
        try:
            cursor.execute(sql)
            self.pyClient.commit()
        except Exception:
            print(sql)
            print(Exception)
            traceback.print_exc()
            self.pyClient.rollback()

    def close(self):
        self.pyClient.close()

def getAttr(content, key, dict, isInt=False, isReplace = True):
    dict[key] = []
    for each in content:
        if each.text:
            if isInt and isReplace:
                dict[key].append(int(each.text.replace('  ', '')))
            elif isInt:
                dict[key].append(int(each.text))
            elif isReplace:
                dict[key].append(each.text.replace('  ', ''))
            else:
                dict[key].append(each.text)

def getAttrText(content, key, dict, regexStr=False):
    dict[key] = []
    for each in content:
        info = each.xpath('string(.)')

        content = info.replace('\n', '').replace('  ', '')
        if regexStr:
            matchObj = re.match(regexStr, content, re.M | re.I)
            if matchObj:
                content = matchObj.group(2)
            else:
                content = ''
        dict[key].append(content)


class dxThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while 1:
            try:
                req = urllib.request.Request('http://daxiaym.com/')
                req.add_header('cache-control', 'no-cache')
                # Customize the default User-Agent header value:
                req.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
                r = urllib.request.urlopen(req)
                selector = etree.HTML(r.read().decode('utf-8'))
                contentDesc = selector.xpath('//*[@id="tab-content"]/div[1]/article/header/h2/a')
                contentUrl = selector.xpath('//*[@id="tab-content"]/div[1]/article/header/h2/a/@href')
                contentStar = selector.xpath('//*[@id="tab-content"]/div[1]/article/header')
                contentJiaoDan = selector.xpath('//*[@id="tab-content"]/div[1]/article/header/b/font[2]')
                contentNianHua = selector.xpath('//*[@id="tab-content"]/div[1]/article/header/b/font[4]')
                # 解析获取数据
                dict = {};
                getAttrText(contentStar, 'p2pname', dict, '(.*?)【(.*?)】')
                getAttr(contentDesc, 'shortdesc', dict)
                dict['url'] = []
                dict['url'].extend(contentUrl)
                getAttrText(contentStar, 'star', dict, '(.*)&nbsp(.*?)&nbsp')

                getAttrText(contentStar, 'longdesc', dict)
                getAttr(contentJiaoDan, 'jiaodan', dict)
                getAttr(contentNianHua, 'nianhua', dict)

                for i in range(len(dict['jiaodan'])):
                    if dict['jiaodan'][i].count('%'):
                        dict['nianhua'].insert(i,dict['jiaodan'][i])
                        dict['jiaodan'][i] = '0'
                #判断是否存在
                db = mysqlClient(MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATA)
                # 先检查各个结构数据是否一致
                goodNum = 0
                # equalStat = EqualStat.Equal;
                intKey = []
                equalValue = []
                for key, value in dict.items():
                    if key == 'p2pname':
                        goodNum = len(value)
                        equalValue.append(key)
                    else:
                        if goodNum == len(value):
                            equalValue.append(key)
                #
                firstHalfSql = 'insert into p2p_info('
                for key in equalValue:
                    firstHalfSql += key + ','
                firstHalfSql += 'status,insertdate,updatedate,source) values('
                for i in range(goodNum):
                    # 先看下库里有没有该产品,有则更新,无则插入
                    sql = "select p2pname from p2p_info where p2pname='%s' and shortdesc='%s' and updatedate > DATE_SUB(NOW(),INTERVAL 240 HOUR) and source='dx' and status=1 " % (pymysql.escape_string(
                        dict['p2pname'][i]),pymysql.escape_string(dict['shortdesc'][i]))
                    if db.query(sql, dict['p2pname'][i]):
                        # 更新值
                        updateSql = "update p2p_info set "
                        updateSql += "updatedate=now() where p2pname='%s' and status=1 and source='dx'" % pymysql.escape_string(
                            dict['p2pname'][i])
                        db.insertOrUpdateGood(updateSql)
                    else:
                        insertSql = firstHalfSql
                        for key, value in dict.items():
                            if key in equalValue:
                                if key in intKey:
                                    insertSql += '%d,' % value[i]
                                else:
                                    insertSql += "'%s'," % pymysql.escape_string(value[i])
                        insertSql += "1,sysdate(),sysdate(),'dx')"
                        db.insertOrUpdateGood(insertSql)
                db.close()
                hour = int(time.strftime("%H", time.localtime()))
                if hour > 0 and hour < 8:
                    time.sleep(3000)
                else:
                    time.sleep(300)
            except Exception:
                print(Exception)
                traceback.print_exc()



class havecaiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while 1:
            try:
                req = urllib.request.Request('http://www.havecai.com//api/tasklist')
                req.add_header('cache-control', 'no-cache')
                # Customize the default User-Agent header value:
                req.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
                r = urllib.request.urlopen(req)
                responseHtml = json.loads(r.read().decode("utf-8"))["data"]
                selector = etree.HTML(responseHtml)
                contentName = selector.xpath('//table[position()<5]/tr[position()>1]/td[1]')
                contentDesc = selector.xpath('//table[position()<5]/tr[position()>1]/td[3]/font')
                contentLongDesc = selector.xpath('//table[position()<5]/tr[position()>1]/td[4]')
                contentUrl = selector.xpath('//table[position()<5]/tr[position()>1]/td[5]/a')
                contentNianHua = selector.xpath('//table[position()<5]/tr[position()>1]/td[2]/font')
                # 解析获取数据
                dict = {};
                getAttr(contentName, 'p2pname', dict)
                getAttr(contentDesc, 'shortdesc', dict)
                getAttr(contentLongDesc, 'longdesc', dict)
                getAttr(contentUrl, 'url', dict)
                getAttr(contentNianHua, 'nianhua', dict)


                #判断是否存在
                db = mysqlClient(MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATA)
                # 先检查各个结构数据是否一致
                goodNum = 0
                # equalStat = EqualStat.Equal;
                intKey = []
                equalValue = []
                for key, value in dict.items():
                    if key == 'p2pname':
                        goodNum = len(value)
                        equalValue.append(key)
                    else:
                        if goodNum == len(value):
                            equalValue.append(key)
                #
                firstHalfSql = 'insert into p2p_info('
                for key in equalValue:
                    firstHalfSql += key + ','
                firstHalfSql += 'status,insertdate,updatedate,source) values('
                for i in range(goodNum):
                    # 先看下库里有没有该产品,有则更新,无则插入
                    sql = "select p2pname from p2p_info where p2pname='%s' and shortdesc='%s' and updatedate > DATE_SUB(NOW(),INTERVAL 240 HOUR) and source='havecai' and status=1 " % (pymysql.escape_string(
                        dict['p2pname'][i]),pymysql.escape_string(dict['shortdesc'][i]))
                    if db.query(sql, dict['p2pname'][i]):
                        # 更新值
                        updateSql = "update p2p_info set "
                        updateSql += "updatedate=now() where p2pname='%s' and status=1 and source='havecai'" % pymysql.escape_string(
                            dict['p2pname'][i])
                        db.insertOrUpdateGood(updateSql)
                    else:
                        insertSql = firstHalfSql
                        for key, value in dict.items():
                            if key in equalValue:
                                if key in intKey:
                                    insertSql += '%d,' % value[i]
                                else:
                                    insertSql += "'%s'," % pymysql.escape_string(value[i])
                        insertSql += "1,sysdate(),sysdate(),'havecai')"
                        db.insertOrUpdateGood(insertSql)
                db.close()
                hour = int(time.strftime("%H", time.localtime()))
                if hour > 0 and hour < 8:
                    time.sleep(3000)
                else:
                    time.sleep(300)
            except Exception:
                print(Exception)
                traceback.print_exc()


class qqcyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while 1:
            try:
                browser = webdriver.Chrome()
                browser.get("https://shimo.im/doc/gu9bjajwawAHFyWD?r=M09X4L/")

                db = mysqlClient(MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATA)
                firstHalfSql = 'insert into p2p_info(p2pname,shortdesc,url,longdesc,nianhua,status,insertdate,updatedate,source) values('
                soup = BeautifulSoup(browser.page_source, 'lxml')
                tables = soup.find_all("table")
                for each in tables:
                    trs = each.find_all("tr")
                    for i in range(len(trs)):
                        if i == 0 or i == len(trs) - 1:
                            continue
                        else:
                            tr = trs[i].find_all("td")
                            info = {}
                            for j in range(len(tr)):
                                info[j]=tr[j].get_text()
                            # 先看下库里有没有该产品,有则更新,无则插入
                            sql = "select p2pname from p2p_info where p2pname='%s' and shortdesc='%s' and updatedate > DATE_SUB(NOW(),INTERVAL 24 HOUR) and source='qqcy' and status=1 " % (pymysql.escape_string(info[1]), pymysql.escape_string(info[2]+":额度:"+info[3]+":返:"+info[4]))
                            if db.query(sql, info[1]):
                                # 更新值
                                updateSql = "update p2p_info set "
                                updateSql += "updatedate=now() where p2pname='%s' and shortdesc='%s' and status=1 and source='qqcy'" % (pymysql.escape_string(info[1]), pymysql.escape_string(info[2]+":额度:"+info[3]+":返:"+info[4]))
                                db.insertOrUpdateGood(updateSql)
                            else:
                                insertSql = firstHalfSql
                                insertSql += "'%s','%s','%s','%s','%s',"%(pymysql.escape_string(info[1]),pymysql.escape_string(info[2]+":额度:"+info[3]+":返:"+info[4]),pymysql.escape_string(info[6]),pymysql.escape_string(info[7]),pymysql.escape_string(info[5]))
                                insertSql += "1,sysdate(),sysdate(),'qqcy')"
                                db.insertOrUpdateGood(insertSql)
                db.close()
                hour = int(time.strftime("%H", time.localtime()))
                if hour > 0 and hour < 8:
                    time.sleep(3000)
                else:
                    time.sleep(300)
            except Exception:
                print(Exception)
                traceback.print_exc()



if __name__ == '__main__':
    threads = []
    dx = dxThread()
    dx.start()
    threads.append(dx)
##
    havecai = havecaiThread()
    havecai.start()
    threads.append(havecai)

    qqcy = qqcyThread()
    qqcy.start()
    threads.append(qqcy)
    # 等待所有线程完成
    for t in threads:
        t.join()