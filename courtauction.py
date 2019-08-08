# -*- coding: utf-8 -*-
__author__ = 'electopx@gmail.com'

import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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

pd_data = pd.DataFrame(columns=['사건번호', '소재지', '용도','감정가', '상태', '매각기일', '유찰수'])
re_td = re.compile(r'(\<td[^>]+[\>])([^<]*)(\<\/td\>)')
re_cancel = re.compile(r'(.+\()([0-9])')

table = soup.find('table', { 'id': 'kyg_list_table' })      # <table id="kyg_list_table">을 찾음
for tr in table.find_all('tr'):                             # 모든 <tr> 태그를 찾아서 반복
    tds = list(tr.find_all('td'))                           # 모든 <td> 태그를 찾아서 리스트로 만듦
    data = []                                               # 데이터를 저장할 리스트 생성
    cancel_number = '0'
    for td in tds:                                          # <td> 태그 리스트 반복
        td_data = ''
        previous_data = ''
        td_text = td.text.replace('\t', '').replace('\n', ' ').strip()
        for item in td.find_all('span'):                    # <td> 안에 <span> 태그가 있으면
            item_data = item.text.replace('\t', '').replace('\n', ' ').strip()
            if item_data.find('현재창') >= 0: continue
            elif item_data.find('건물') >= 0 and item_data.find('토지') is -1:
                td_data += ' ' + item_data + ' [토지 ]'
            elif previous_data.find(item_data) is -1:
                if td_data is not '':
                    td_data += ' ' + item_data
                else:
                    td_data += item_data
            previous_data = item_data                       # <span> 태그 안에서 데이터를 가져옴
        if td_data is '':
            item_data = re.sub('(\<\/td\>)', '', re.sub('(\<td[^>]+[\>])', '', str(td))).strip()
            if item_data.find('<') is -1:
                td_data += item_data
        if (td_text.find('진행') is not -1 or td_text.find('취하') is not -1) and td_text.find('(') is not -1:
            cancel_number = re.search(re_cancel, td_text).group(2)
        if td_data is not '': data.append(td_data)          # data 리스트에 td 데이터 저장
    data.append(cancel_number)
    if len(data) is 7: pd_data.loc[len(pd_data)] = data

# '매각기일' 데이터 처리
pd_data['매각기일'] = pd_data['매각기일'].str.split(' ', n=0, expand=True)[0].str.strip()

# '감정가','최저가' 데이터 처리
temp_data = pd_data['감정가'].str.split(' ', n=0, expand=True)
appraisalPrice = temp_data[0].str.strip()                   # 감정가
minPrice = temp_data[1].str.strip()                         # 최저가
pd_data['감정가'] = appraisalPrice
pd_data.insert(4, '최저가', minPrice)                        # 4th index에 column 추가
#print (pd_data['감정가'])
#print (pd_data['최저가'])

# '소재지' 데이터 처리
temp_data = pd_data['소재지'].str.split('[', n=0, expand=True)
pd_data['소재지'] = temp_data[0].str.strip()                 # 소재지
pd_data.insert(2, '건물', temp_data[1].str.replace('건물 ','').str.replace(']','').str.strip())          # 2th index에 column 추가
pd_data.insert(3, '토지', temp_data[2].str.replace('토지 ','').str.replace(']','').str.strip())          # 3rd index에 column 추가
pd_data.insert(4, '특수조건', temp_data[3].str.replace(']','').str.strip())                              # 4th index에 column 추가

# '소재지(도로명)', '행정구역코드', '도로명코드' 데이터 처리
area_data = []
road_data = []
underground_data = []
new_address_data = []
building_data = []
sub_building_data = []
re_area = re.compile(r'(<admCd>)([0-9]+)')
re_road = re.compile(r'(<rnMgtSn>)([0-9]+)')
re_underground = re.compile(r'(<udrtYn>)([0-9]+)')
re_building = re.compile(r'(<buldMnnm>)([0-9]+)')
re_sub_building = re.compile(r'(<buldSlno>)([0-9]+)')
re_address = re.compile(r'(^.+[가-힣]+([동]|[로0-9번길])\s)[0-9\-]+')
driver.get('http://www.juso.go.kr/addrlink/devAddrLinkRequestUse.do?menu=roadSearch')
for i in range(len(pd_data)):
    address = re.search(re_address, pd_data.loc[i].소재지).group(0)
    driver.find_element_by_xpath('//*[@id="keywordRoad"]').click()
    driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(Keys.CONTROL, 'a')
    driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(address)
    driver.find_element_by_xpath('//*[@id="formRoadSearch"]/fieldset[1]/div[2]/a').click()             # 체험하기
    driver.implicitly_wait(1)
    # '소재지(도로명)'
    new_address = driver.find_element_by_xpath('//*[@id="listRoadSearch"]/table/tbody/tr/td/p[2]').text
    new_address_data.append(new_address)
    driver.find_element_by_xpath('//*[@id="listRoadSearch"]/p/a').click()                              # 검색결과형식보기
    # '행정구역코드'
    area = re.search(re_area, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
    area_data.append(area)
    # '도로명코드'
    road = re.search(re_road, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
    road_data.append(road)
    # '지하여부'
    underground = re.search(re_underground, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
    underground_data.append(underground)
    # '건물본번'
    building = re.search(re_building, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
    building_data.append(building)
    # '건물부번'
    sub_building = re.search(re_sub_building, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
    sub_building_data.append(sub_building)
    # HOME
    driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(Keys.HOME)
pd_data.insert(2, '소재지(도로명)', new_address_data)
pd_data.insert(3, '행정구역코드', area_data)
pd_data.insert(4, '도로명코드', road_data)
pd_data.insert(5, '지하여부', underground_data)
pd_data.insert(6, '건물본번', building_data)
pd_data.insert(7, '건물부번', sub_building_data)

print (pd_data)
driver.close()

# information for DB
user = 'user'
password = ''
host = ''
port = ''
structure = ''
table = ''

args = sys.argv[0:]
optionLen = len(args)

def init():

    global user, password, host, port, structure, table

    if (len(args) <= 1):
        print('[ERR] There is no option')
        return False

    # Command
    # python main.py --user xxxx --password 'xxxx' --host 'xx.xx.xx.xx' --port xxxx --structure xxxx --table xxxx
    for i in range(optionLen-1):
        data = str(args[i+1])
        if args[i].lower() == '--user':		    # --user : user name of MySQL (e.g.: root)
            user = data
        elif args[i].lower() == '--password':	# --password : password of username
            password = data
        elif args[i].lower() == '--host':	    # --host : host of MySQL (e.g.: 127.0.0.1)
            host = data
        elif args[i].lower() == '--port':	    # --port : port of mySQl (e.g.: 3306)
            port = data
        elif args[i].lower() == '--structure':	# --structure : structure name (e.g.: wordpress)
            structure = data
        elif args[i].lower() == '--table':	    # --table : table name (e.g.: wp_custom_xxx)
            table = data

    if (user == '') or (password == '') or (host == '') or (port == '') or (structure == '') or (table == ''):
        print('[ERR] Please input all required data like user, password, host, port, structure and table name.')
        return False

    return True

if init():
    try:
        # Accessing the DB
        engine = create_engine('mysql+pymysql://'+user+':'+password+'@'+host+':'+port+'/'+structure, encoding='utf-8')
        # Entering data into the DB
        pd_data.to_sql(name=table, con=engine, if_exists = 'replace')
        print('[OK] Connection success')

    # Exception for connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('[ERR] Something is wrong with your user name or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('[ERR] Database structure does not exist')
        else:
            print('[ERR]', err)
else:
    print("[ERR] Connection failure")
