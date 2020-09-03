# Feb23, 2020, ms
# flask_for_Haya2_webscraping.py
# place this on 3B2

from flask import Flask
from flask import jsonify

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


# === flask server ===
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
'''
according to https://flask.palletsprojects.com/en/0.12.x/config/
By default Flask serialize object to ascii-encoded JSON.
If this is set to False Flask will not encode to ASCII and
output strings as-is and return unicode strings.
jsonify will automatically encode it in utf-8 then for
transport for instance.
'''

@app.route('/haya2')
def haya2():
    # get time_since_launch, earth_to_hayabusa from web
    time_since_launch, earth_to_hayabusa = getHaya2Data()
    return_dict = {'time_since_launch': time_since_launch,
                   'earth_to_hayabusa': earth_to_hayabusa}
    return jsonify(return_dict)


# === web scraping function ===
def getHaya2Data():
    # ref is webscraping2.py
    # ブラウザのオプションを格納する変数をもらってきます。
    options = Options()
    # Headlessモードを有効にする
    options.headless = True
    # ブラウザを起動する
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',
                              options=options)
    print('implicitly_wait for 10 seconds from now.')
    driver.implicitly_wait(10)
    # ブラウザでアクセスする
    driver.get("http://www.hayabusa2.jaxa.jp/en/")
    print('sleep 5 seconds from now.')
    time.sleep(5)
    # HTMLを文字コードをUTF-8に変換してから取得します。
    html = driver.page_source.encode('utf-8')
    # BeautifulSoupで扱えるようにパースします
    soup = BeautifulSoup(html, "html.parser")

    # table parsing
    time_since_launch = "+0d"
    earth_to_hayabusa = "0.00"
    # get a table
    table = soup.findAll("table")[0]
    tbody = table.find("tbody")
    trs = tbody.find_all("tr")
    for tr in trs:
        th = tr.find("th")
        td = tr.find("td")
        # get only
        # Time since launch
        # and
        # Earth to Hayabusa2
        if th.text == "Time since launch":
            time_since_launch = td.text.split(' ')[0]
            print(time_since_launch)
        elif th.text == "Earth to Hayabusa2":
            earth_to_hayabusa = td.text.split('×')[0]
            print(earth_to_hayabusa)  # wow! × is not x!!!
            # I copied it from below and paste it in above line.

    return time_since_launch, earth_to_hayabusa


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
