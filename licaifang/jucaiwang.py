#!/usr/bin/python3
# -*- coding:UTF-8 -*-

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
def sendmail():
    # 输入Email地址和口令:
    from_addr = ""
    password = ""
    # 输入SMTP服务器地址:
    smtp_server = ""
    # 输入收件人地址:
    to_addr = ""

    message = MIMEText('jucaiwang...', 'plain', 'utf-8')

    subject = 'jucaiwang'
    message['Subject'] = Header(subject, 'utf-8')

    server = smtplib.SMTP(smtp_server, 25)
    server.ehlo()
    server.starttls()
    #server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], message.as_string())
    server.quit()
    sys.exit()


while 1 :
    hour = int(time.strftime("%H", time.localtime()));
    if hour > 8 and hour < 19:
        req = urllib.request.Request('https://www.1ju.com/1-37-c-1-q-3-n-0-j-0-m-%E8%AF%B7%E8%BE%93%E5%85%A5%E9%A1%B9%E7%9B%AE%E5%90%8D%E7%A7%B0.html')
        req.add_header('cache-control', 'no-cache')
        # Customize the default User-Agent header value:
        req.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
        r = urllib.request.urlopen(req)
        selector = etree.HTML(r.read().decode('utf-8'))
        content = selector.xpath('//*[@class="itemlist"]/div[1]/div[2]/div[4]/a')
        for each in content:
            if each.text != '已满标':
                sendmail()
        time.sleep(5)
    else:
        time.sleep(300)

