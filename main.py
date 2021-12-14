from PIL import ImageGrab
from pyzbar.pyzbar import ZBarSymbol
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import numpy as np
import pyzbar.pyzbar as pyzbar
import cv2, time

username =  ''
password = ''

apspaceLink = 'https://apspace.apu.edu.my/'
apspaceDashboard = 'https://apspace.apu.edu.my/tabs/dashboard'
apspaceAttendix = 'https://apspace.apu.edu.my/attendix/update'

def main():
    print('Start Tracking Attendance...\n')
    lastSignTime = time.time()
    lastOtpCode = None
    while True:
        otpCode = getOtpCode()
        dateTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if lastOtpCode is None:
            print(dateTime + ' OTP CODE FOUND -> ' + otpCode)
            signAttendance(otpCode)
            lastOtpCode = otpCode
            lastSignTime = time.time()
            print('Done Signing Attendance\n')
        if lastOtpCode == otpCode:
            lastSignGap = time.time() - lastSignTime
            if lastSignGap >  300.0:
                signAttendance(otpCode)
                lastSignTime = time.time()
        if lastOtpCode != otpCode:
            print(dateTime + ' OTP CODE FOUND -> ' + otpCode)
            signAttendance(otpCode)
            lastSignTime = time.time()
            print('Done Signing Attendance\n')


def getOtpCode():
    while True:
        img = ImageGrab.grab()
        imgNp = np.array(img)
        frame = cv2.cvtColor(imgNp, cv2.COLOR_BGR2GRAY)
        decodedData = pyzbar.decode(frame, symbols=[ZBarSymbol.QRCODE])
        sorted(ZBarSymbol.__members__.keys())
        for obj in decodedData:
            otpCode = obj.data.decode('utf-8')
            if len(otpCode) > 1:
                return otpCode

def signAttendance(otpCode):
    element = 'ion-button'
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    s = Service('./chromedriver.exe')
    browser = webdriver.Chrome(service=s, options=options)
    browser.get(apspaceLink)
    browser.implicitly_wait(10)

    get_ion_button = browser.find_elements(By.TAG_NAME, element)
    get_ion_button[1].click()

    get_apkey = browser.find_elements(By.NAME, "apkey")
    get_password = browser.find_elements(By.NAME, "password")
    get_apkey[1].send_keys(username)
    get_password[1].send_keys(password)
    get_ion_button[2].click()

    WebDriverWait(browser, 15).until(EC.url_to_be(apspaceDashboard))
    time.sleep(1)
    get_all_button = browser.find_elements(By.TAG_NAME, element)
    get_all_button[3].click()

    WebDriverWait(browser, 15).until(EC.url_to_be(apspaceAttendix))
    get_input = browser.find_elements(By.TAG_NAME, "input")

    for i in range(3):
        get_input[i+1].send_keys(otpCode[i])

    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "ion-alert")))
    click_button = browser.find_element(By.CLASS_NAME, "alert-button").click()

main()