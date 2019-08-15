# -*- coding: utf-8 -*-
__author__ = 'electopx@gmail.com'

import re
import math
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import sys
import datetime
import dateutil.relativedelta
import mysql.connector
from sqlalchemy import create_engine
from mysql.connector import errorcode

pd.options.mode.chained_assignment = None  # default='warn'

# the value of pandas to string
def to_str(var):
    return str(list(np.reshape(np.asarray(var), (1, np.size(var)))[0]))[1:-1].replace("'", '')

# Finding index of new address
def find_index(jibun, text):
    index = 0
    juso_data = re.split(r'[ ](?=<jibunAddr>)', text)
    for juso in juso_data:
        juso = re.sub(r'(<\/jibunAddr>[\s\w\W]+)', '', juso[11:])
        if jibun in juso: break
        else: index += 1

    return index

def get_juso(index, text):
    if index > 0: return re.split(r'[ ](?=<juso>)', text)[index]
    else: return text

# 실행 초기화
def init():
    args = sys.argv[0:]
    optionLen = len(args)
    global user, password, host, port, key, structure, table_name

    if (len(args) <= 1):
        print('[ERR] There is no option')
        return False

    # Command
    # python main.py --user xxxx --password 'xxxx' --host 'xx.xx.xx.xx' --port xxxx --structure xxxx --table xxxx --key 'xxxx'
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
        elif args[i].lower() == '--key':	    # --key : OPen API key (e.g.: 9ActTOxJHu43bYcBJRqA3rM4nzaC4k...)
            key = data
        elif args[i].lower() == '--structure':	# --structure : structure name (e.g.: wordpress)
            structure = data
        elif args[i].lower() == '--table':	    # --table : table name (e.g.: wp_custom_xxx)
            table_name = data

    if (password == '') or (host == '') or (port == '') or (key == '') or (structure == '') or (table_name == ''):
        print('[ERR] Please input all required data like user, password, host, port, key, structure and table name.')
        return False

    return True

# 공공데이터포털 > 국토교통부 실거래가 정보 > 아파트매매 실거래 상세자료
# https://www.data.go.kr/dataset/3050988/openapi.do
def getActualPrice(apt_data, year, month, code, key):
    date = str(year)
    if month < 10: date += '0' + str(month)
    else: date += str(month)
    url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade'
    url += '?&LAWD_CD=' + code + '&DEAL_YMD=' + date + '&serviceKey=' + key

    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome('../driver/chromedriver', options=options)
    driver.get(url)
    
    # Beautiful Soup
    xml_file = driver.page_source
    xml_soup = BeautifulSoup(xml_file, 'lxml-xml')
    xml = xml_soup.find_all('item')
    #apt_data = pd.DataFrame(columns=['년', '월', '일', '거래금액', '건축년도', '법정동', '아파트', '전용면적', '지번', '지역코드', '층'])

    for apt in xml:
        item_data = []
        item_data.append(apt.find('년').text.strip())
        item_data.append(apt.find('월').text.strip())
        item_data.append(apt.find('일').text.strip())
        item_data.append(apt.find('거래금액').text.strip())
        item_data.append(apt.find('건축년도').text.strip())
        item_data.append(apt.find('법정동').text.strip())
        item_data.append(apt.find('아파트').text.strip())
        item_data.append(apt.find('전용면적').text.strip())
        item_data.append(apt.find('지번').text.strip())
        item_data.append(apt.find('지역코드').text.strip())
        item_data.append(apt.find('층').text.strip())
        apt_data.loc[len(apt_data)] = item_data

    driver.close()
    return apt_data

# information for DB
user, password, host, port, key= 'user', '', '', '', ''
structure, table_name = '', ''

if init():
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
    driver.implicitly_wait(1)
    driver.find_element_by_xpath('//*[@id="list_limit"]').click()
    driver.find_element_by_xpath('//*[@id="list_limit_combo"]/li[6]/nobr').click()

    # 텍스트 보기
    driver.implicitly_wait(1)
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
    appraisalPrice = temp_data[0].str.replace(',', '').str.strip()     # 감정가
    minPrice = temp_data[1].str.replace(',', '').str.strip()           # 최저가
    pd_data['감정가'] = appraisalPrice
    pd_data.insert(4, '최저가', minPrice)
    #print (pd_data['감정가'])
    #print (pd_data['최저가'])

    # '소재지', '층수', '동', '호' 데이터 처리
    ho = []
    dong = []
    floor = []
    re_dong = re.compile(r'([0-9]+동)')
    re_ho = re.compile(r'([0-9]+호)')
    re_floor = re.compile(r'([0-9]+층)')
    temp_data = pd_data['소재지'].str.split('[', n=0, expand=True)
    for element in pd_data['소재지']:
        ho_data = re.search(re_ho, element)
        dong_data = re.search(re_dong, element)
        floor_data = re.search(re_floor, element)
        if floor_data: floor.append(floor_data.group(0))
        else: floor.append(None)
        if dong_data: dong.append(dong_data.group(0))
        else: dong.append(None)
        if ho_data: ho.append(ho_data.group(0))
        else: ho.append(None)
    pd_data['소재지'] = temp_data[0].str.replace(r'([0-9]+(번지|층))', '').str.replace(r'[ ]+', ' ').str.strip()     # 소재지
    pd_data.insert(3, '층수', floor)
    pd_data.insert(4, '동', dong)
    pd_data.insert(5, '호', ho)
    pd_data.insert(6, '건물', temp_data[1].str.replace('건물 ','').str.replace(']','').str.strip())
    pd_data.insert(7, '토지', temp_data[2].str.replace('토지 ','').str.replace(']','').str.strip())
    pd_data.insert(8, '특수조건', temp_data[3].str.replace(']','').str.strip())

    # '소재지(도로명)', '행정구역코드', '도로명코드' 데이터 처리
    area_data, road_data, underground_data, new_address_data, building_data = [], [], [], [], []
    sub_building_data, jibun_data, sub_jibun_data, building_name_data, dong_name_data = [], [], [], [], []
    re_area = re.compile(r'(<admCd>)([0-9]+)')
    re_road = re.compile(r'(<rnMgtSn>)([0-9]+)')
    re_underground = re.compile(r'(<udrtYn>)([0-9]+)')
    re_jibun = re.compile(r'(<lnbrMnnm>)([0-9]+)')
    re_sub_jibun = re.compile(r'(<lnbrSlno>)([0-9]+)')
    re_building = re.compile(r'(<buldMnnm>)([0-9]+)')
    re_sub_building = re.compile(r'(<buldSlno>)([0-9]+)')
    re_building_name = re.compile(r'(<bdNm>)([가-힣0-9. ]+)')
    re_dong_name = re.compile(r'(<emdNm>)([가-힣0-9]+)')
    re_address = re.compile(r'(^.+[가-힣]+([동]|[로0-9번길])\s)[0-9\-]+')
    driver.get('http://www.juso.go.kr/addrlink/devAddrLinkRequestUse.do?menu=roadSearch')

    for i in range(len(pd_data)):
        address = re.search(re_address, pd_data.loc[i].소재지).group(0)
        jibun = re.search(r'[0-9\-]+$', address).group(0)
        driver.find_element_by_xpath('//*[@id="keywordRoad"]').click()
        driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(Keys.CONTROL, 'a')
        driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(address)
        driver.find_element_by_xpath('//*[@id="formRoadSearch"]/fieldset[1]/div[2]/a').click()                      # 체험하기
        driver.implicitly_wait(1)
        driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(Keys.HOME)        
        driver.find_element_by_xpath('//*[@id="listRoadSearch"]/p/a').click()                                       # 검색결과형식보기 > 열기
        index = find_index(jibun, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text)               # Getting index
        if index > 1: index_str = '['+str(index)+']'
        else: index_str = ''
        # '소재지(도로명)'
        new_address = driver.find_element_by_xpath('//*[@id="listRoadSearch"]/table/tbody/tr'+index_str+'/td/p[2]').text
        new_address_data.append(new_address)
        # xml <juso> data
        juso = get_juso(index, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text)
        # '법정동'
        #dong_name = re.search(re_dong_name, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text)
        dong_name = re.search(re_dong_name, juso)
        if dong_name is not None and dong_name.group(0) is not '<emdNm>': dong_name_data.append(dong_name.group(2))
        else: dong_name_data.append(None)
        # '아파트'
        #building_name = re.search(re_building_name, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text)
        #if building_name is not None and building_name.group(0) is not '<bdNm>': building_name_data.append(building_name.group(2).replace('아파트', '').replace(' ', ''))
        #else: building_name_data.append(None)
        building_name = re.search(re_building_name, juso)
        if building_name is not None and building_name.group(0) is not '<bdNm>': building_name_data.append(building_name.group(2).replace('아파트', '').replace(' ', ''))
        else: building_name_data.append(None)
        # '행정구역코드'
        #area = re.search(re_area, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        area = re.search(re_area, juso).group(2)
        area_data.append(area)
        # '도로명코드'
        #road = re.search(re_road, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        road = re.search(re_road, juso).group(2)
        road_data.append(road)
        # '지하여부'
        #underground = re.search(re_underground, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        underground = re.search(re_underground, juso).group(2)
        underground_data.append(underground)
        # '지번'
        #jibun = re.search(re_jibun, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        #sub_jibun = re.search(re_sub_jibun, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        #if sub_jibun is not '0': jibun += '-' + sub_jibun
        jibun_data.append(jibun)
        # '건물본번'
        #building = re.search(re_building, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        building = re.search(re_building, juso).group(2)
        building_data.append(building)
        # '건물부번'
        #sub_building = re.search(re_sub_building, driver.find_element_by_xpath('//*[@id="dataListRoadSearch"]').text).group(2)
        sub_building = re.search(re_sub_building, juso).group(2)
        sub_building_data.append(sub_building)
        # HOME
        driver.find_element_by_xpath('//*[@id="keywordRoad"]').send_keys(Keys.HOME)

    driver.close()

    pd_data.insert(2, '소재지(도로명)', new_address_data)
    pd_data.insert(4, '법정동', dong_name_data)
    pd_data.insert(5, '아파트', building_name_data)
    pd_data.insert(12, '행정구역코드', area_data)
    pd_data.insert(13, '도로명코드', road_data)
    pd_data.insert(14, '지하여부', underground_data)
    pd_data.insert(15, '지번', jibun_data) 
    pd_data.insert(16, '건물본번', building_data)
    pd_data.insert(17, '건물부번', sub_building_data)

    # '상태' 데이터 처리
    temp_data = pd_data['상태'].str.split(' ', n=0, expand=True)
    pd_data['상태'] = temp_data[0].str.strip()
    pd_data.insert(21, '최저가율', temp_data[1].str.strip())

    # '전용면적' 데이터 처리
    dedicated_area_data = []
    temp_data = pd_data['건물'].str.replace('평', '').str.replace(',', '').astype(float)
    for temp in temp_data:
        dedicated_area = round(temp * 3.30579, 2)
        dedicated_area_data.append(dedicated_area)
    pd_data.insert(9, '전용면적', dedicated_area_data)

    # 실거래가 데이터 수집
    now = datetime.datetime.now()
    apt_data = pd.DataFrame(columns=['년', '월', '일', '거래금액', '건축년도', '법정동', '아파트', '전용면적', '지번', '지역코드', '층'])
    codes = pd_data['행정구역코드'].str[:5]
    codes = codes.drop_duplicates()
    for i, code in codes.iteritems():
        for j in range(6):      # 최근 6개월간 데이터 수집
            now_delta = now + dateutil.relativedelta.relativedelta(months=-j)
            getActualPrice(apt_data, now_delta.year, now_delta.month, code, key)

    # '건축년도' 데이터 처리
    pd_data.insert(6, '건축년도', None)
    for i in range(len(pd_data)):
        if pd_data['건축년도'].iloc[i] is None:
            temp_dong = pd_data['법정동'].iloc[i]
            temp_jibun = pd_data['지번'].iloc[i]
            built_years = apt_data['건축년도'].loc[(apt_data['법정동'] == temp_dong) & (apt_data['지번'] == temp_jibun)]
            if len(built_years) > 0:
                built_years = built_years.drop_duplicates()
                built_year = to_str(built_years.iloc[0]).replace("'", '')
                pd_data['건축년도'].loc[(pd_data['법정동'] == temp_dong) & (pd_data['지번'] == temp_jibun)] = built_year

    # '전용면적' 데이터 처리
    pd_data.insert(10, '전용면적(국토부)', None)
    for i in range(len(pd_data)):
        temp_dong = pd_data['법정동'].iloc[i]
        temp_jibun = pd_data['지번'].iloc[i]
        area_data = apt_data['전용면적'].loc[(apt_data['법정동'] == temp_dong) & (apt_data['지번'] == temp_jibun)]
        if len(area_data) > 0:
            area_data = area_data.drop_duplicates()
            old_area = float(to_str(pd_data['전용면적'].iloc[i]))
            for j in range(len(area_data)):
                new_area = float(to_str(area_data.iloc[j]))
                gap = abs(old_area - new_area)
                if gap < 1: pd_data['전용면적(국토부)'].loc[(pd_data['법정동'] == temp_dong) & (pd_data['지번'] == temp_jibun)] = new_area

    # '실거래최고가', '실거래평균가', '실거래최저가', '실거래수' 데이터 처리
    pd_data.insert(23, '실거래최고가', None)
    pd_data.insert(24, '실거래평균가', None)
    pd_data.insert(25, '실거래최저가', None)
    pd_data.insert(26, '실거래수', None)
    for i in range(len(pd_data)):
        temp_dong = pd_data['법정동'].iloc[i]
        temp_jibun = pd_data['지번'].iloc[i]
        temp_area = pd_data['전용면적(국토부)'].iloc[i]
        price_data = pd.to_numeric(apt_data['거래금액'].loc[(apt_data['법정동'] == temp_dong) & (apt_data['지번'] == temp_jibun) & (apt_data['전용면적'] == str(temp_area))].str.replace(',',''))
        if len(price_data) > 0:
            price_high = price_data.max()*10000
            price_average = price_data.mean().round(1)*10000
            price_low = price_data.min()*10000
            price_number = len(price_data)
            pd_data['실거래최고가'].loc[(pd_data['법정동'] == temp_dong) & (pd_data['지번'] == temp_jibun) & (pd_data['전용면적(국토부)'] == temp_area)] = price_high
            pd_data['실거래평균가'].loc[(pd_data['법정동'] == temp_dong) & (pd_data['지번'] == temp_jibun) & (pd_data['전용면적(국토부)'] == temp_area)] = price_average
            pd_data['실거래최저가'].loc[(pd_data['법정동'] == temp_dong) & (pd_data['지번'] == temp_jibun) & (pd_data['전용면적(국토부)'] == temp_area)] = price_low
            pd_data['실거래수'].loc[(pd_data['법정동'] == temp_dong) & (pd_data['지번'] == temp_jibun) & (pd_data['전용면적(국토부)'] == temp_area)] = price_number

    # Checking final results
    apt_data.to_csv('actualPrice.csv', index=False, sep=';', encoding='utf-8')
    pd_data.to_csv('auctionData.csv', index=False, sep=';', encoding='utf-8')
    print (pd_data)
    print (apt_data)

    # Accessing the DB
    try:
        engine = create_engine('mysql+pymysql://'+user+':'+password+'@'+host+':'+port+'/'+structure, encoding='utf-8')

        # Entering data into the DB
        pd_data.to_sql(name=table_name, con=engine, if_exists = 'replace')
        print('[OK] Execution success')

    # Exception for the DB connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('[ERR] Something is wrong with your user name or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('[ERR] Database structure does not exist')
        else:
            print('[ERR]', err)

else:
    print("[ERR] Execution failure")
