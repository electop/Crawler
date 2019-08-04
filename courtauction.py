# -*- coding: utf-8 -*-
__author__ = 'electopx@gmail.com'

import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import sys
import datetime
import mysql.connector
from sqlalchemy import create_engine
from mysql.connector import errorcode

#driver = webdriver.Chrome('../driver/chromedriver')
#driver = webdriver.PhantomJS('../driver/phantomjs')
options = webdriver.ChromeOptions()
#options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
driver = webdriver.Chrome('../driver/chromedriver', options=options)

driver.get('http://www.xn--289a10kw0fb2e5xnhho.com/workdir/upcate/kyg/kyg_srch.php?fcate=kyg&sub_menu_name=%C1%BE%C7%D5%B0%CB%BB%F6&tnm=1http://www.xn--289a10kw0fb2e5xnhho.com/workdir/upcate/kyg/kyg_srch.php?fcate=kyg&sub_menu_name=%C1%BE%C7%D5%B0%CB%BB%F6&tnm=1http://www.xn--289a10kw0fb2e5xnhho.com/workdir/upcate/kyg/kyg_srch.php?fcate=kyg&sub_menu_name=%C1%BE%C7%D5%B0%CB%BB%F6&tnm=1')
driver.find_element_by_name('sido').send_keys('경기')
driver.find_element_by_name('gugun').send_keys('수원시')
driver.find_element_by_xpath('//*[@id="rltyct1"]').click()  # 아파트
driver.find_element_by_xpath('//*[@id="rltyct2"]').click()  # 주택
driver.find_element_by_xpath('//*[@id="rltyct7"]').click()  # 오피스텔
driver.find_element_by_xpath('//*[@id="kyg_srch_option"]/table/tbody/tr[9]/td/input[1]').click()    # 검색하기

# 100개씩
driver.implicitly_wait(3)
driver.find_element_by_xpath('//*[@id="list_limit"]').click()
driver.find_element_by_xpath('//*[@id="list_limit_combo"]/li[6]/nobr').click()

# 텍스트 보기
driver.implicitly_wait(3)
driver.find_element_by_xpath('//*[@id="kyg_list"]/table[1]/tbody/tr/td[8]').click()

# 결과 화면을 이미지로 저장
#driver.save_screenshot('./images/001.png')

# Beautiful Soup
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

#raw_list = soup.find_all('tr', 'kyg_list_style')
#raw_list = soup.find_all('td', 'status')
#status_list = [raw_list[n].find('span').get_text() for n in range(0, len(raw_list))]
#print (status_list)

pd_data = pd.DataFrame(columns=['사건번호', '소재지', '용도','감정가/최저가', '상태', '매각기일'])
re_td = re.compile(r'(\<td[^>]+[\>])([^<]*)(\<\/td\>)')

table = soup.find('table', { 'id': 'kyg_list_table' })      # <table id="kyg_list_table">을 찾음
for tr in table.find_all('tr'):                             # 모든 <tr> 태그를 찾아서 반복
    tds = list(tr.find_all('td'))                           # 모든 <td> 태그를 찾아서 리스트로 만듦
    data = []                                               # 데이터를 저장할 리스트 생성
    for td in tds:                                          # <td> 태그 리스트 반복
        td_data = ''
        previous_data = ''
        for item in td.find_all('span'):                    # <td> 안에 <span> 태그가 있으면
            item_data = item.text.replace('\t', '').replace('\n', ' ').strip()
            if item_data.find('현재창') >= 0: continue
            if previous_data.find(item_data) is -1:
                if td_data is not '':
                    td_data += ' ' + item_data
                else:
                    td_data += item_data
            previous_data = item_data                       # <span> 태그 안에서 데이터를 가져옴
        if td_data is '':
            item_data = re.sub('(\<\/td\>)', '', re.sub('(\<td[^>]+[\>])', '', str(td))).strip()
            if item_data.find('<') is -1:
                td_data += item_data
        if td_data is not '': data.append(td_data)          # data 리스트에 td 데이터 저장
    if len(data) is 6: pd_data.loc[len(pd_data)] = data
print (pd_data)
#print (pd_data['감정가/최저가'])
driver.close()

user = 'user'
password = ''
host = ''
database = ''
config = {}

args = sys.argv[0:]
optionLen = len(args)

def init():

    global user, password, host, database, config

    if (len(args) <= 1):
        print('[ERR] There is no option')
        return False

    for i in range(optionLen-1):
        data = str(args[i+1])
        if args[i].upper() == '-U':		# -U : user name of MySQL (e.g.: root)
            user = data
        elif args[i].upper() == '-P':	# -P : password of username
            password = data
        elif args[i].upper() == '-H':	# -H : host of MySQL (e.g.: 127.0.0.1)
            host = data
        elif args[i].upper() == '-D':	# -D : database name (e.g.: wp_aitest)
            database = data

    if (user == '') or (password == '') or (host == '') or (database == ''):
        print('[ERR] Please input all required data like user, password, host and database name.')
        return False

    return True

if init():
    try:
        engine = create_engine('mysql+pymysql://'+user+':'+password+'@'+host+':3306/'+database, encoding='utf-8')
        pd_data.to_sql(name='interauction', con=engine, if_exists = 'replace')
        print('[OK] Connection success')

    # Exception for connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('[ERR] Something is wrong with your user name or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('[ERR] Database does not exist')
        else:
            print('[ERR]', err)
else:
    print("[ERR] Connection failure")
