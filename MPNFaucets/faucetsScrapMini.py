import csv
import json
import logging
import multiprocessing
import os
import platform
import time
from concurrent.futures.thread import ThreadPoolExecutor
from random import randint
from selenium.webdriver import ActionChains
from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
import re
from bs4 import BeautifulSoup

# ------------------------------------------------------------
try:
    os.makedirs("logs")
except:
    pass
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('logs/all.log')
# file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)


# ------------------------------------------------------------


def searchPageData(categID, prodState=False):
    driver = seleniumLiteTrigger(headlessState=prodState)
    try:
        driver.get(f"https://www.faucet.com/search?term={categID}&r=24&s=_relevance&p=1")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))
        except:
            pass
        response_text = str(driver.page_source)
        driver.quit()
    except Exception as e:
        driver.quit()
    soup = BeautifulSoup(response_text, 'html.parser')
    urlSet = soup.find_all("div", class_="item")[0].find_all("a")[0].attrs["href"]
    return "https://www.faucet.com"+urlSet



def seleniumLiteTrigger(headlessState=True):
    options = Options()
    options.headless = headlessState
    with open("vpn.config.json") as json_data_file:
        configs = json.load(json_data_file)
    VPN_User = configs['VPN_User']
    VPN_Pass = configs['VPN_Pass']
    VPN_IP = configs['VPN_IP_US'][randint(0, len(configs['VPN_IP_US']) - 1)]
    VPN_Port = configs['VPN_Port']

    # Web Content Fetcher
    proxies = {
        "http": f"http://{VPN_User}:{VPN_Pass}@{VPN_IP}:{VPN_Port}",
        "https": f"http://{VPN_User}:{VPN_Pass}@{VPN_IP}:{VPN_Port}",
    }
    credData = VPN_User + ':' + VPN_Pass
    optionsProx = {
        'proxy': {
            'http': 'http://' + credData + '@' + f"{VPN_IP}:{VPN_Port}",
            'https': 'https://' + credData + '@' + f"{VPN_IP}:{VPN_Port}"
        }
    }
    if "Windows" in str(platform.system()):
        # WINDOWS
        geckoPath = r"driver\geckodriver.exe"
        moz_profPath = r"C:\Users\SaGe\AppData\Roaming\Mozilla\Firefox\Profiles\jbz9m3sj.default"
        # driver = webdriver.Firefox(options=options, executable_path=geckoPath)
    elif "Linux" in str(platform.system()):
        # Linux
        geckoPath = r"driver/geckodriver_linux"
        moz_profPath = r"/home/sage/.mozilla/firefox/hdby1exf.default-release-1601650032565"
    else:
        # Mac
        geckoPath = r"driver/geckodriver"
        moz_profPath = r"/Users/SaGe/Library/Application Support/Firefox/Profiles/24po1ob3.default-release"
    #
    logger.debug("Mozilla profile path : " + moz_profPath)
    logger.debug("Mozilla gecko path : " + geckoPath)
    driver = webdriver.Firefox(options=options, executable_path=geckoPath,
                               service_log_path="logs/selenium.gecko.log")
    # driver = webdriver.Firefox(options=options, seleniumwire_options=optionsProx, executable_path=geckoPath,
    #                            service_log_path="logs/selenium.gecko.log")
    return driver


def prodData(url,categID, prodState=True):
    driver =seleniumLiteTrigger(headlessState=prodState)
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))
        except:
            pass
        response_text = str(driver.page_source)
        driver.quit()
    except Exception as e:
        driver.quit()
    print("Hi")


    soup = BeautifulSoup(response_text, 'html.parser')
    prodDataS = {}
    for x in soup.find_all("ul",class_="js-finishes")[1].find_all("li"):
        prodDataSet = {}

        # Product Name
        prodDataSet["MPN"] = categID
        prodDataSet["URL"] = url
        prodDataSet['variant image'] = x.find_all("div",class_="w-third")[0].find_all("img")[0].attrs["src"]
        prodDataSet['price'] = x.find_all("div",class_="w-two-thirds")[0].find_all("div")[1].text
        prodDataSet['finish'] = x.find_all("div",class_="w-two-thirds")[0].find_all("div")[0].text

        prodDataSet["title"] = soup.find("h1", attrs={"data-automation": "heading"}).text

        # Image 1,2,3,4 etc.
        prodDataSet["images"] = [x.attrs["src"] for x in
                                 soup.find("div", attrs={"id": "PDP-Media-Gallery-Image"}).find_all("img")]

        # Model No.
        prodDataSet["model"] = soup.find("span", attrs={"id": "heading", "class": "b"}).text

        # Finish
        tmpJson = json.loads(re.findall("\"eVar\"\:(\{[^}]+\})", str(response_text))[0])
        # finishName = tmpJson.keys()
        # for x in [x for x in tmpJson if len(tmpJson[x]) == 0]:
        #     del tmpJson[x]
        #
        finish = "Unavailable"
        for xa in tmpJson:
            if tmpJson[xa].count(":") > 1:
                prodDataSet["finish"] = tmpJson[xa].split(":")[2]
                break

        # Product Overview
        prodDataSet["overviewRAW"] = str(soup.find("div", attrs={"class": "js-overview-details"}))

        # Product Overview Text Only
        prodDataSet["overviewText"] = soup.find("div", attrs={"class": "js-overview-details"}).text

        # Description

        # Manufcaturer Resource:
        prodDataSet["manuRes"] = {x.text: x.attrs["data-href"].replace("//", "") for x in
                                  soup.find("div", attrs={"id": "manufacturer-resources"}).find_all("a")}

        # Dimensions and Measurements

        for a, b in enumerate(soup.find("div", attrs={"id": "product-specs"}).find_all("h4", attrs={"class": "mt4"})):
            prodDataSet[b.text] = {
                x.find("div", attrs={"class": "specs-key"}).text: x.find("div", attrs={"class": "specs-value"}).text for
                x in
                soup.find("div", attrs={"id": "product-specs"}).find_all("div", attrs={"class": "mt2"})[
                    a].find_all("div", attrs={"class": "striped--grey-light"})}



        prodDataS[x.find_all("div",class_="w-two-thirds")[0].find_all("div")[0].text] =prodDataSet

    return prodDataS

def csvWrite(finalData):
    with open(f"Faucets MPN Data.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(finalData)

def dedup(inArr):
    res = []
    for i in inArr:
        if i not in res:
            res.append(i)
    return res

def singleCore(categID, prodState=True):
    if len(categID) > 2:
        atmptA = 0
        while atmptA < 5:
            try:
                time.sleep(randint(100,500)/200)
                url = searchPageData(categID, prodState=prodState)
                break
            except Exception as e:
                atmptA += 1
                print(e)
                if atmptA == 4:
                    raise Exception(f"No data for {categID}")

        atmpt = 0
        while atmpt < 5:
            try:
                # products[categID] = prodData(url)
                time.sleep(randint(100,500)/200)
                outData = {categID:prodData(url,categID, prodState = prodState)}
                break
            except Exception as e:
                atmpt += 1
                print("Reattempt ", url, e)
        return outData

if __name__ == '__main__':
    with open("MPNs.txt","r") as categFile:
        categIDs = categFile.read().split("\n")

    with open("curlData.txt","r") as fileCurl:
        curlData = fileCurl.read()

    # products = {}
    # for categID in categIDs:
    #     pass
    #     try:
    #         products[categID] = singleCore(categID)[categID]
    #     except Exception as e:
    #         print(e)


    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()*2) as executor:
        results = []
        for categID in categIDs[:2]:
            if len(categID) > 2:
                # break
                dataOut = executor.submit(singleCore, categID, False)
                results.append(dataOut)
        executor.shutdown(wait=True)

    products = {}
    for x in results:
        try:
            products[list(x.result().keys())[0]] = x.result()[list(x.result().keys())[0]]
        except Exception as e:
            print(e)



    with open(f"Faucets MPN Data.json" , "w") as file:
        json.dump(products, file, indent=3)

    mainheaders = []
    subheaders = []
    for x in products:
        for y in products[x]:
            for z in products[x][y]:
                if type(products[x][y][z]) is dict:
                    for a in products[x][y][z]:
                        subheaders.append(z + "\n" + a)
                else:
                    mainheaders.append(z)
    mainheaders = dedup(mainheaders)
    subheaders = sorted(list(set(subheaders)))
    headers = mainheaders + subheaders

    bodyData = []
    for a in products:
        for b in products[a]:
            rowData = []
            for x in headers:
                if "\n" in x:
                    try:
                        rowData.append(products[a][b][x.split("\n")[0]][x.split("\n")[1]])
                    except:
                        rowData.append("")
                else:
                    rowData.append(products[a][b][x])
            bodyData.append(rowData)

    finalData = [headers] + bodyData

    csvWrite(finalData)
