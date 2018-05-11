

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
import threading
from enum import Enum
from mysql_config import *

class EqualStat(Enum):
    Equal = 1
    notEqual = 2
    shortNotEqual = 3

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

def getAttrText(content, key, dict, isInt = False, isReplace=True):
    dict[key] = []
    for each in content:
        info = each.xpath('string(.)')
        if isReplace:
            content = info.replace('\n', '').replace('  ', '').replace('','')
        else:

            content = info
        if isInt:
            dict[key].append(int(content))
        else:
            dict[key].append(content)



class mmbThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while 1:
            try:
                req = urllib.request.Request('http://www.manmanbuy.com/')
                req.add_header('cache-control', 'no-cache')
                # Customize the default User-Agent header value:
                req.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
                r = urllib.request.urlopen(req)
                selector = etree.HTML(r.read().decode('gbk'))
                contentTitle = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[3]/a')
                contentPrice = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[4]/a')
                contentUrl = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[1]/a/@href')
                # contentSupport = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[1]/span[1]')
                # contentShortDesc = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[2]/strong[1]')
                # contentLongDesc = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[2]')

                # info = data[0].xpath('string(.)')
                # content = info.replace('\n', '')
                # contentDesc = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[2]/text()')
                contentZhi = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[2]/a[2]/span')
                contentBuZhi = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[2]/a[3]/span')
                # contentFav = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/a[1]/span')
                # contentComment = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/a[2]/text()')
                contentComment = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[2]/a[1]')
                contentTime = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[5]/span[2]')
                contentSource = selector.xpath('/html/body/div[4]/div/div[3]/div[2]/div[2]/ul/li/div[5]/span[1]')
                # contentBuyUrl = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[2]/div/div/a/@href')

                # 解析获取数据
                dict = {};
                getAttr(contentTitle, 'title', dict)
                getAttr(contentPrice, 'price', dict)
                dict['url'] = []
                dict['url'].extend(contentUrl)

                # getAttr(contentSupport, 'support', dict)
                # getAttr(contentShortDesc, 'shortdesc', dict)
                # getAttrText(contentLongDesc, 'longdesc', dict)
                # getAttr(contentShortDesc, 'longdesc', dict, True)
                getAttr(contentZhi, 'zhi', dict, True)
                getAttr(contentBuZhi, 'buzhi', dict, True)
                # getAttr(contentFav, 'fav', dict, True)
                getAttrText(contentComment, 'comment_number', dict, True)

                # 时间
                getAttr(contentTime, 'show_time', dict, False, False)
                getAttr(contentSource, 'source', dict)
                # 购买链接
                # getAttr(contentBuyUrl, 'buyurl', dict)

                db = mysqlClient(MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATA)
                # 先检查各个结构数据是否一致
                goodNum = 0
                #equalStat = EqualStat.Equal;
                intKey = ['zhi','buzhi','comment_number']
                equalValue = []
                for key, value in dict.items():
                    if key == 'title':
                        goodNum = len(value)
                        equalValue.append(key)
                    else:
                        if goodNum == len(value):
                            equalValue.append(key)
                #
                firstHalfSql = 'insert into smzdm_www_info('
                for key in equalValue:
                    firstHalfSql += key + ','
                firstHalfSql += 'insertdate,www) values('

                for i in range(goodNum):
                    # 先看下库里有没有该产品,有则更新,无则插入
                    sql = "select title from smzdm_www_info where title='%s' and insertdate > DATE_SUB(NOW(),INTERVAL 12 HOUR)" % pymysql.escape_string(
                        dict['title'][i])
                    if db.query(sql, dict['title'][i]):
                        # 更新值
                        updateSql = "update smzdm_www_info set "
                        if 'zhi' in equalValue:
                            updateSql += 'zhi=%d,' % dict['zhi'][i]
                        if 'buzhi' in equalValue:
                            updateSql += 'buzhi=%d,' % dict['buzhi'][i]
                        if 'comment_number' in equalValue:
                            updateSql += 'comment_number=%d,' % dict['comment_number'][i]
                        updateSql += "updatedate=now() where insertdate > DATE_SUB(NOW(),INTERVAL 12 HOUR) and title='%s'"%  pymysql.escape_string(dict['title'][i])
                        db.insertOrUpdateGood(updateSql)
                    else:
                        insertSql = firstHalfSql
                        for key, value in dict.items():
                            if key in equalValue:
                                if key in intKey:
                                    insertSql+='%d,'% value[i]
                                else:
                                    insertSql += "'%s',"% pymysql.escape_string(value[i])
                        insertSql += "sysdate(),'mmb')"
                        db.insertOrUpdateGood(insertSql)
                db.close()
                hour = int(time.strftime("%H", time.localtime()))
                if hour > 0 and hour < 8:
                    time.sleep(90)
                else:
                    time.sleep(20)
            except Exception:
                print(Exception)
                traceback.print_exc()


class smzdmThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while 1:
            req = urllib.request.Request('https://www.smzdm.com/')
            req.add_header('cache-control', 'no-cache')
            # Customize the default User-Agent header value:
            req.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
            r = urllib.request.urlopen(req)
            selector = etree.HTML(r.read().decode('utf-8'))
            contentTitle = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/h5/a')
            contentPrice = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/h5/a/span')
            contentUrl = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/h5/a/@href')
            contentSupport = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[1]/span[1]')
            contentShortDesc = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[2]/strong[1]')
            contentLongDesc = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[2]')

            # info = data[0].xpath('string(.)')
            # content = info.replace('\n', '')
            # contentDesc = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[2]/text()')
            contentZhi = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/span/a[1]/span[1]/span')
            contentBuZhi = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/span/a[2]/span[1]/span')
            contentFav = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/a[1]/span')
            # contentComment = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/a[2]/text()')
            contentComment = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[1]/a[2]')
            contentTime = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[2]/span')
            contentSource = selector.xpath(
                '//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[2]/span/a')
            # contentBuyUrl = selector.xpath('//*[@id="feed-main-list"]/li[starts-with(@class,"feed-row-wide  ")]/div/div[2]/div[3]/div[2]/div/div/a/@href')

            # 解析获取数据
            dict = {};
            getAttr(contentTitle, 'title', dict)
            getAttr(contentPrice, 'price', dict)
            dict['url'] = []
            dict['url'].extend(contentUrl)

            getAttr(contentSupport, 'support', dict)
            getAttr(contentShortDesc, 'shortdesc', dict)
            getAttrText(contentLongDesc, 'longdesc', dict)
            # getAttr(contentShortDesc, 'longdesc', dict, True)
            getAttr(contentZhi, 'zhi', dict, True)
            getAttr(contentBuZhi, 'buzhi', dict, True)
            getAttr(contentFav, 'fav', dict, True)
            getAttrText(contentComment, 'comment_number', dict, True)

            # 时间
            getAttr(contentTime, 'show_time', dict)
            getAttr(contentSource, 'source', dict)
            # 购买链接
            # getAttr(contentBuyUrl, 'buyurl', dict)

            db = mysqlClient(MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATA)
            # 先检查各个结构数据是否一致
            goodNum = 0
            #equalStat = EqualStat.Equal;
            intKey = ['zhi','buzhi','fav','comment_number']
            equalValue = []
            for key, value in dict.items():
                if key == 'title':
                    goodNum = len(value)
                    equalValue.append(key)
                else:
                    if goodNum == len(value):
                        equalValue.append(key)
            #
            firstHalfSql = 'insert into smzdm_www_info('
            for key in equalValue:
                firstHalfSql += key + ','
            firstHalfSql += 'insertdate,www) values('
            for i in range(goodNum):
                # 先看下库里有没有该产品,有则更新,无则插入
                sql = "select title from smzdm_www_info where title='%s' and insertdate > DATE_SUB(NOW(),INTERVAL 12 HOUR)" % pymysql.escape_string(
                    dict['title'][i])
                if db.query(sql, dict['title'][i]):
                    # 更新值
                    updateSql = "update smzdm_www_info set "
                    if 'zhi' in equalValue:
                        updateSql += 'zhi=%d,' % dict['zhi'][i]
                    if 'buzhi' in equalValue:
                        updateSql += 'buzhi=%d,' % dict['buzhi'][i]
                    if 'fav' in equalValue:
                        updateSql += 'fav=%d,' % dict['fav'][i]
                    if 'comment_number' in equalValue:
                        updateSql += 'comment_number=%d,' % dict['comment_number'][i]
                    updateSql += "updatedate=now() where insertdate > DATE_SUB(NOW(),INTERVAL 12 HOUR) and title='%s'"%  pymysql.escape_string(dict['title'][i])
                    db.insertOrUpdateGood(updateSql)
                else:
                    insertSql = firstHalfSql
                    for key, value in dict.items():
                        if key in equalValue:
                            if key in intKey:
                                insertSql+='%d,'% value[i]
                            else:
                                insertSql += "'%s',"% pymysql.escape_string(value[i])
                    insertSql += "sysdate(),'smzdm')"
                    db.insertOrUpdateGood(insertSql)
            db.close()
            hour = int(time.strftime("%H", time.localtime()))
            if hour > 0 and hour < 8:
                time.sleep(90)
            else:
                time.sleep(20)
if __name__ == '__main__':
    threads = []
    smzdm = smzdmThread()
    smzdm.start()
    threads.append(smzdm)

    mmb = mmbThread()
    mmb.start()
    threads.append(mmb)
    # 等待所有线程完成
    for t in threads:
        t.join()
