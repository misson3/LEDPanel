from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time

session = HTMLSession()
resp = session.get("http://www.hayabusa2.jaxa.jp/en/")
resp.html.render(sleep=3, timeout=20)

bsObj = BeautifulSoup(resp.html.html, "html.parser")

table = bsObj.findAll("table")[0]
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

'''
Time since launch: +1886d 08:16:56
Total distance travelled: 4594542.88×103 km
Earth to Hayabusa2: 249133.71×103 km
Velocity relative to the Sun: 25.28km/s
Radio wave round trip: 1661sec
'''
