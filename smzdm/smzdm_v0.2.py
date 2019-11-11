#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import time
import pymysql

chrome_opt = Options()      # 创建参数设置对象.
chrome_opt.add_argument('--headless')   # 无界面化.
chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
chrome_opt.add_argument('--window-size=1366,768')   # 设置窗口大小, 窗口大小会有影响.

# 创建Chrome对象并传入设置信息.
driver = webdriver.Chrome(chrome_options=chrome_opt)
# 操作这个对象.

# 打开数据库连接
db = pymysql.connect("ip", "user", "password", "zhidemai")
# 使用cursor()方法获取操作游标
cursor = db.cursor()
while True:
    driver.get('https://www.smzdm.com/')
    time.sleep(1)
    selector = etree.HTML(driver.page_source)

    title_data = selector.xpath('//*[@id="feed-main-list"]/li/div/div[2]/h5/a/text()')

    goods_size = len(title_data) + 1

    for j in range(1,goods_size):
        xpath_frame = '//*[@id="feed-main-list"]/li[' + str(j) + ']/div/div[2]'
        total_data = selector.xpath(xpath_frame)
        for i in total_data:
            zhi = (i.xpath('./div[4]/div[1]/span/a[1]/span[1]/span/text()'))#值
            if len(zhi) == 0:
                continue
            link =(i.xpath('./h5/a/@href'))   # 链接
            title = (i.xpath('./h5/a/text()')) #标题
            sub_title = (i.xpath('./div[1]/a/text()'))#副标题
            buzhi = (i.xpath('./div[4]/div[1]/span/a[2]/span[1]/span/text()'))#不值
            pub_time = (i.xpath('./div[4]/div[2]/span/text()'))#时间
            #print('=========================================================')
            # SQL 更新语句
            try:
                new_title = title[0].replace("'", "*", 20)
                new_sub_title = sub_title[0].replace("'", "*", 20)
                new_link = link[0].replace("'", "*", 20)
                new_pub_time = pub_time[0].strip().replace("'", "*", 20)
                querysql = "SELECT count(1) FROM zhidemai \
                            WHERE title = '%s' and sub_title = '%s' " % (str(new_title), str(new_sub_title))
                cursor.execute(querysql)
                results = cursor.fetchall()
                for row in results:
                    count = row[0]
                if count == 0:
                    sql = "INSERT INTO zhidemai(title, \
                           sub_title, link, zhi, buzhi, time, update_time ) \
                           VALUES ('%s', '%s',  '%s',  %d,  %d, '%s', now())" % \
                          (str(new_title), str(new_sub_title), str(new_link), int(zhi[0]), int(buzhi[0]), str(new_pub_time))
                else:
                    sql = "update zhidemai set zhi=%d, buzhi=%d,last_update_time=now() where title = '%s' and sub_title = '%s'" %( int(zhi[0]), int(buzhi[0]),str(new_title), str(new_sub_title))

                # 执行SQL语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except:
                # 发生错误时回滚
                db.rollback()
                print(querysql)
                print(sql)
    time.sleep(25)
driver.quit()   # 使用完, 记得关闭浏览器, 不然chromedriver.exe进程为一直在内存中.
# 关闭数据库连接
db.close()
