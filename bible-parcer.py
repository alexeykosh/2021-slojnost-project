from selenium import webdriver
from bs4 import BeautifulSoup
import time
from random import randint

url = ('https://www.bible.com/bible/2834/'\
	'LUK.19.%EA%95%A2%EA%95%8C%EA%94%B3')
lang = 'vai'

driver = webdriver.Firefox()
driver.get(url)

while True:
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find_all(class_='reader')
    res = ''.join(e for e in table[0].text.lower() if e.isalnum())
    with open(lang + '.txt', 'a+') as file:
        file.writelines(res)
    try:
        url = driver.current_url
        driver.find_element_by_css_selector('html.i-amphtml-singledoc.'\
        	'i-amphtml-standalone body.sans-serif.mv6.amp-mode-mouse'\
        	' div.body.mt5 div.mw6.center.pa3.pt4.pb7.mt6 a.bible-nav-'\
        	'button.fixed.br-100.ba.b--yv-gray15.bg-white.flex.'\
        	'items-center.justify-center.nav-right.right-1').click()
        time.sleep(randint(1, 10))
    except:
        break

driver.quit()
