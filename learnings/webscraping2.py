from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

# ブラウザのオプションを格納する変数をもらってきます。
options = Options()

# Headlessモードを有効にする（コメントアウトするとブラウザが実際に立ち上がります）
#options.set_headless(True)
options.headless = True

# ブラウザを起動する
driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)
print('implicitly_wait for 10 seconds from now.')
driver.implicitly_wait(10)

# ブラウザでアクセスする
driver.get("http://www.hayabusa2.jaxa.jp/en/")
#driver.get("https://www.raspberrypi.org/")
print('sleep 5 seconds from now.')
time.sleep(5)

# HTMLを文字コードをUTF-8に変換してから取得します。
html = driver.page_source.encode('utf-8')

# BeautifulSoupで扱えるようにパースします
soup = BeautifulSoup(html, "html.parser")

#print(soup)
# idがheikinの要素を表示
#print(soup.select_one("#heikin"))
#bsObj = BeautifulSoup(resp.html.html, "html.parser")
#table = soup.findAll("table")[0]
table = soup.findAll("table")[0]
#print(table)

#table = bsObj.findAll("table")[0]
tbody = table.find("tbody")
trs = tbody.find_all("tr")

for tr in trs:
    th = tr.find("th")
    td = tr.find("td")
    #print(th.text, ': ', td.text, sep='')
    # get only
    # Time since launch
    # and
    # Earth to Hayabusa2
    if th.text == "Time since launch":
        print(td.text.split(' ')[0])
    elif th.text == "Earth to Hayabusa2":
        print(td.text.split('×')[0])  # wow! × is not x!!!
        # I copied it from below and paste it in above line.
