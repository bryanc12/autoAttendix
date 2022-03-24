import gc
import json
import time
from datetime import datetime

import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from PIL import ImageGrab
from pyzbar.pyzbar import ZBarSymbol
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

apspaceLink = 'https://apspace.apu.edu.my/'
apspaceDashboard = 'https://apspace.apu.edu.my/tabs/dashboard'
apspaceAttendix = 'https://apspace.apu.edu.my/attendix/update'

def main():
    username, password = getCredentials()
    if (username == '') or (password == ''):
        print('Please fill in your username & password!')
        exit()

    print('Start Tracking Attendance...\n')
    lastSignTime = time.time()
    lastOtpCode = None

    while True:
        otpCode = getOtpCode()
        
        if lastOtpCode is None:
            otpFound(otpCode)
            signAttendance(otpCode, username, password)
            lastOtpCode = otpCode
            lastSignTime = time.time()
        if lastOtpCode == otpCode:
            lastSignGap = time.time() - lastSignTime
            if lastSignGap >  300.0:
                otpFound(otpCode)
                signAttendance(otpCode, username, password)
                lastOtpCode = otpCode
                lastSignTime = time.time()
            time.sleep(5)
        if lastOtpCode != otpCode:
            otpFound(otpCode)
            signAttendance(otpCode, username, password)
            lastOtpCode = otpCode
            lastSignTime = time.time()
        gc.collect()

def getCredentials():
    data = json.loads(open('.\credentials.json', 'r').read())
    return(data['username'], data['password'])

def getOtpCode():
    while True:
        try:
            img = ImageGrab.grab()
        except OSError:
            print('Screen capture permission denied by Operating System, error handled and solved.\n')
        imgNp = np.array(img)
        frame = cv2.cvtColor(imgNp, cv2.COLOR_BGR2GRAY)
        decodedData = pyzbar.decode(frame, symbols=[ZBarSymbol.QRCODE])
        sorted(ZBarSymbol.__members__.keys())
        for obj in decodedData:
            otpCode = obj.data.decode('utf-8')
            if otpCode.isdecimal():
                if (len(otpCode) > 0) and (len(otpCode) < 4):
                    return otpCode
        gc.collect()
        time.sleep(1)

def otpFound(otpCode):
    dateTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    otpFound = (dateTime + ' OTP CODE FOUND -> ' + otpCode)
    print(otpFound)
    log((otpFound + '\n'))

def signAttendance(otpCode, username, password):
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service('./chromedriver.exe')
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(apspaceLink)
    browser.implicitly_wait(10)

    get_ion_button = browser.find_elements(By.TAG_NAME, "ion-button")
    get_ion_button[1].click()

    browser.find_elements(By.NAME, "apkey")[1].send_keys(username)
    browser.find_elements(By.NAME, "password")[1].send_keys(password)
    get_ion_button[2].click()

    WebDriverWait(browser, 15).until(EC.url_to_be(apspaceDashboard))
    time.sleep(1)
    browser.find_element(By.CLASS_NAME, "quick-access-attendance").click()

    WebDriverWait(browser, 15).until(EC.url_to_be(apspaceAttendix))
    get_input = browser.find_elements(By.TAG_NAME, "input")

    for i in range(3):
        get_input[i+1].send_keys(otpCode[i])

    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "ion-alert")))
    time.sleep(1)

    alertMessage = browser.find_element(By.CLASS_NAME, "alert-message").get_attribute("innerHTML") + '\n'
    print(alertMessage)
    log((alertMessage + '\n\n'))
    browser.find_element(By.CLASS_NAME, "alert-button").click()

def log(msg):
    logFile = open("latest.log", "a")
    logFile.write(msg)

main()