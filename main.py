from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from PIL import Image, ImageChops

from base64 import b64decode

from dateutil import parser


class NaverShopping():
    def __init__(self):
        self.storeType = '' #brand | smartstore
        self.marketName = ''
        self.productId = ''
        self.driver = None
        self.buyButton = None
        self.optionButton = None
        self.optionList = []
        self.payPassword = ''
        self.pwButtons = [None] * 10
        self.images = []

        self.loadImages()

    def loadDriver(self):
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_setting_values': {'images': 2 }}
        options.add_experimental_option('prefs', prefs)
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=options)


    def loadImages(self):
        for i in range(10):
            self.images.append(Image.open(f'n_{i}.png'))

    def setProductInfo(self, storeType, marketName, productId):
        self.storeType = storeType
        if not storeType in ('smartstore', 'brand'): raise Exception('Incorrect Store Type')
        self.marketName = marketName
        self.productId = productId

    def setPayPassword(self, pw):
        self.payPassword = pw

    def openNaverLogin(self):
        self.driver.get('https://nid.naver.com/nidlogin.login');

    def openStore(self):
        self.driver.get(f'https://{self.storeType}.naver.com/{self.marketName}/products/{self.productId}')

    def clickOption(self):
        self.optionButton = self.driver.find_element_by_css_selector('#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div > a')
        self.optionButton.click()
        self.optionList = self.driver.find_elements_by_css_selector('#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div > ul > li')
        for option in self.optionList:
            if '품절' in option.text: continue
            option.click()
            break


    def findBuyButton(self, waitTime):
        t = time.time()
        while True:
            try:
                self.buyButton = self.driver.find_element_by_css_selector('fieldset > div > div:nth-child(1) > div > a._2-uvQuRWK5')
            except:
                if time.time() - t > waitTime: return False
            else:
                return True

    def getPwButtons(self):
        buttons = []
        btnImgB64 = ''
        while True:
            try:
                buttons = self.driver.find_elements_by_css_selector('#keyboard > table > tbody > tr > td > button > span')[:-1]
                btnImgB64 = buttons[0].get_attribute('style').split(',')[1][:-3]
            except: continue
            else: break

        with open('temp.png', 'wb') as f:
            f.write(b64decode(btnImgB64))

        img = Image.open('temp.png')

        idx = 0
        for y in range(0, 200, 50):
            for x in range(0, 120, 40):
                newImg = img.crop((x, y, x + 40, y + 50))
                j = 0
                for targetImg in self.images:
                    diff = ImageChops.difference(newImg, targetImg)
                    if not diff.getbbox():
                        #idx = int((y / 50) * 3 + x / 40)
                        self.pwButtons[j] = buttons[idx]
                        idx += 1
                        break
                    j += 1

    def buy(self):
        #self.clickOption()
        self.buyButton.click()
        payButton = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btn_payment'))
        )
        #self.driver.find_element_by_css_selector('#ecouponAutoCheckbox').click()
        payButton.click()

        win_main = self.driver.window_handles[0]

        WebDriverWait(self.driver, 3).until(EC.new_window_is_opened(self.driver.window_handles))

        win_next = self.driver.window_handles[1]

        self.driver.switch_to.window(win_next)

        WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.ID, 'keyboard'))
        )

        self.getPwButtons()

        for i in self.payPassword:
            self.pwButtons[int(i)].click()

        self.driver.switch_to.window(win_main)

class NaverMacro():
    def __init__(self):
        self.nShopping = NaverShopping()

        self.nShopping.loadDriver()

        self.targetTime = None

        #self.driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')

        self.currentTime = 0

        #self.openClock()

    def openClock(self):
        self.driver.get('https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%EB%84%A4%EC%9D%B4%EB%B2%84+%EC%8B%9C%EA%B3%84')

    def getTime(self):
        return ''.join(self.driver.find_element_by_css_selector('#_cs_domestic_clock > div._timeLayer.time_bx > div > div').text.split())

    def setMacro(self, startTime, storeType, marketName, productId, pwTextDir):
        self.nShopping.setProductInfo(storeType, marketName, productId)
        with open(pwTextDir, 'r') as f:
            self.nShopping.setPayPassword(f.read())
        self.nShopping.openNaverLogin()
        input('Please enter if you logged in')
        self.nShopping.openStore()
        input('Enter to start')

        '''
        while True:
            self.targetTime = parser.parse(startTime)
            currentTime = parser.parse(self.getTime())
            timeDelta = currentTime.timestamp() - self.targetTime.timestamp()
            if -20 <= timeDelta <= 300: break
        '''

        while True:
            self.nShopping.openStore()
            if not self.nShopping.findBuyButton(0.3): continue
            #self.nShopping.clickOption()
            self.nShopping.buy()
            time.sleep(100)
            
                

if __name__ == '__main__':
    a = NaverMacro()
    a.setMacro('11:00:00AM', 'brand', 'samlip', '6510954368', 'pw.txt')
