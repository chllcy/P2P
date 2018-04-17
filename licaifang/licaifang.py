#!/usr/bin/python3


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
import json
import re

def sendmail():
    # 输入Email地址和口令:
    from_addr = ""
    password = ""
    # 输入SMTP服务器地址:
    smtp_server = ""
    # 输入收件人地址:
    to_addr = ""

    message = MIMEText('licaifang...', 'plain', 'utf-8')

    subject = 'licaifang'
    message['Subject'] = Header(subject, 'utf-8')

    server = smtplib.SMTP(smtp_server, 25)
    server.ehlo()
    server.starttls()
    #server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], message.as_string())
    server.quit()
    sys.exit()


url = "http://www.licaifan.com/project/list"

payload = "{page:1,period_type:3}"
headers = {
    'content-type': "application/json",
    'cache-control': "no-cache"
    }
while 1 :
    hour = int(time.strftime("%H", time.localtime()));
    if hour > 8 and hour < 21:
        data = bytes(payload, 'utf8')
        request = urllib.request.Request(url, data, headers=headers)
        response = urllib.request.urlopen(request)
        response_json = json.loads(response.read().decode("utf-8"))
        for each in response_json['project']:
            pattern = re.compile(r'\d+')  # 查找数字
            period = pattern.findall(each['period'])
            if each['available_amount'] > '0' and int(period[0]) < 100:
                sendmail()
        sendmail()
        time.sleep(5)
    else:
        time.sleep(300)

