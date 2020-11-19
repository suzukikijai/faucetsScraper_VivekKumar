import csv
import json
import multiprocessing
import time
from concurrent.futures.thread import ThreadPoolExecutor
from random import randint

import requests
import re
from bs4 import BeautifulSoup

def searchPageData(categID):
    headers = {
        'authority': 'www.faucet.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': re.findall(r"cookie: ([^\n]+)'", curlData)[0]
    }

    params = (
        ('term', f'{categID}'),
        ('r', '24'),
        ('s', '_relevance'),
        ('p', '1'),
    )

    response = requests.get('https://www.faucet.com/search', headers=headers, params=params)
    data = response.text
    soup = BeautifulSoup(response.text, 'html.parser')
    urlSet = soup.find_all("div", class_="item")[0].find_all("a")[0].attrs["href"]
    return "https://www.faucet.com"+urlSet

def prodData(url,categID):
    headers = {
        'authority': 'www.faucet.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': re.findall(r"cookie: ([^\n]+)'", curlData)[0]
    }

    response = requests.get(url, headers=headers)
    data = response.text
    soup = BeautifulSoup(response.text, 'html.parser')
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
        tmpJson = json.loads(re.findall("\"eVar\"\:(\{[^}]+\})", str(response.text))[0])
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


def singleCore(categID):
    if len(categID) > 2:
        atmptA = 0
        while atmptA < 5:
            try:
                time.sleep(randint(100,500)/200)
                url = searchPageData(categID)
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
                outData = {categID:prodData(url,categID)}
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

    products = {}
    for categID in categIDs:
        pass
        try:
            products[categID] = singleCore(categID)[categID]
        except Exception as e:
            print(e)


    # with ThreadPoolExecutor(max_workers=(10)) as executor:
    #     results = []
    #     for categID in categIDs:
    #         pass
    #         dataOut = executor.submit(singleCore, categID)
    #         results.append(dataOut)
    #     executor.shutdown(wait=True)
    #
    # products = {}
    # for x in results:
    #     try:
    #         products[list(x.result().keys())[0]] = x.result()[list(x.result().keys())[0]]
    #     except Exception as e:
    #         print(e)
        # products = singleCore(categID)
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
