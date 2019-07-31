import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select

#driver = webdriver.Chrome('../driver/chromedriver')
#driver = webdriver.PhantomJS('../driver/phantomjs')
options = webdriver.ChromeOptions()
#options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
driver = webdriver.Chrome('../driver/chromedriver', options=options)
driver.get('http://www.xn--289a10kw0fb2e5xnhho.com/workdir/upcate/kyg/kyg_srch.php?fcate=kyg&sub_menu_name=%C1%BE%C7%D5%B0%CB%BB%F6&tnm=1http://www.xn--289a10kw0fb2e5xnhho.com/workdir/upcate/kyg/kyg_srch.php?fcate=kyg&sub_menu_name=%C1%BE%C7%D5%B0%CB%BB%F6&tnm=1http://www.xn--289a10kw0fb2e5xnhho.com/workdir/upcate/kyg/kyg_srch.php?fcate=kyg&sub_menu_name=%C1%BE%C7%D5%B0%CB%BB%F6&tnm=1')
#driver.implicitly_wait(3)
driver.find_element_by_name('sido').send_keys('경기')
driver.find_element_by_name('gugun').send_keys('수원시')
driver.find_element_by_xpath('//*[@id="rltyct1"]').click()
driver.find_element_by_xpath('//*[@id="rltyct2"]').click()
driver.find_element_by_xpath('//*[@id="rltyct7"]').click()
driver.find_element_by_xpath('//*[@id="kyg_srch_option"]/table/tbody/tr[9]/td/input[1]').click()

driver.implicitly_wait(3)
driver.find_element_by_xpath('//*[@id="list_limit"]').click()
driver.find_element_by_xpath('//*[@id="list_limit_combo"]/li[6]/nobr').click()
driver.implicitly_wait(3)
driver.find_element_by_xpath('//*[@id="kyg_list"]/table[1]/tbody/tr/td[8]').click()

#driver.save_screenshot('./images/001.png')

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

#raw_list = soup.find_all('tr', 'kyg_list_style')
#raw_list = soup.find_all('td', 'status')
#status_list = [raw_list[n].find('span').get_text() for n in range(0, len(raw_list))]
#print (status_list)

table = soup.find('table', { 'id': 'kyg_list_table' })      # <table id="kyg_list_table">을 찾음
data = []                                                   # 데이터를 저장할 리스트 생성
for tr in table.find_all('tr'):                             # 모든 <tr> 태그를 찾아서 반복
    tds = list(tr.find_all('td'))                           # 모든 <td> 태그를 찾아서 리스트로 만듦
    for td in tds:                                          # <td> 태그 리스트 반복
        for item in td.find_all('span'):
            td_data = item.text
            data.append(td_data)
        #if td.find('span'):                                 # <td> 안에 <span> 태그가 있으면
        #    td_data = td.find('span').text                  # <span> 태그 안에서 데이터를 가져옴
        #    data.append(td_data)                            # data 리스트에 td 데이터 저장

print (data)

driver.close()
