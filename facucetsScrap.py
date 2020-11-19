import csv
import json

import requests
import re
from bs4 import BeautifulSoup

def numberOfPages(categID, curlData):
    headers = {
        'authority': 'www.faucet.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'accept': '*/*',
        'dnt': '1',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://www.faucet.com/kitchen-faucets/c{categID}?r=48&s=SCORE&p=2&categoryId={categID}',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': re.findall(r"cookie: ([^\n]+)'", curlData)[0]
    }

    params = (
        ('r', '100'),
        ('s', 'SCORE'),
        ('p', '1'),
        ('categoryId', categID),
    )

    response = requests.get('https://www.faucet.com/app/api/search/products', headers=headers, params=params)
    return response.json()["pagination"]['numberOfPages']

def searchPageData(pageNum, categID):
    headers = {
        'authority': 'www.faucet.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'accept': '*/*',
        'dnt': '1',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://www.faucet.com/kitchen-faucets/c{categID}?r=48&s=SCORE&p=2&categoryId={categID}',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': re.findall(r"cookie: ([^\n]+)'", curlData)[0]
    }

    params = (
        ('r', '100'),
        ('s', 'SCORE'),
        ('p', f'{pageNum}'),
        ('categoryId', categID),
    )

    response = requests.get('https://www.faucet.com/app/api/search/products', headers=headers, params=params)
    jsonData = response.json()["products"]

    urlSet = []
    for x in response.json()["products"]:
        urlSet.append("https://www.faucet.com"+x['productLink'])
    return urlSet

def prodData(url):
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
    soup = BeautifulSoup(response.text, 'html.parser')

    prodDataSet = {}

    # Product Name
    prodDataSet["URL"] = url
    prodDataSet["title"] = soup.find("h1", attrs={"data-automation":"heading"}).text

    # Image 1,2,3,4 etc.
    prodDataSet["images"] = [x.attrs["src"] for x in soup.find("div", attrs={"id":"PDP-Media-Gallery-Image"}).find_all("img")]

    # Price
    prodDataSet["price"] = soup.find("span", attrs={"class":"text-price"}).text

    # Sale Price if available
    prodDataSet["salePrice"] = soup.find("span", attrs={"class":"text-price"}).text

    # Model No.
    prodDataSet["model"] = soup.find("span", attrs={"id":"heading","class":"b"}).text

    # From the collection
    prodDataSet["collectName"] = soup.find("a", attrs={"data-automation":"top-collection-link"}).text

    # Finish
    tmpJson = json.loads(re.findall("\"eVar\"\:(\{[^}]+\})",str(response.text))[0])
    # finishName = tmpJson.keys()
    # for x in [x for x in tmpJson if len(tmpJson[x]) == 0]:
    #     del tmpJson[x]
    #
    finish = "Unavailable"
    for x in tmpJson:
        if tmpJson[x].count(":") > 1:
            prodDataSet["finish"] = tmpJson[x].split(":")[2]
            break

    # Product Overview
    prodDataSet["overviewRAW"] = str(soup.find("div", attrs={"class": "js-overview-details"}))

    # Product Overview Text Only
    prodDataSet["overviewText"] = soup.find("div", attrs={"class": "js-overview-details"}).text

    # Description

    # Manufcaturer Resource:
    prodDataSet["manuRes"] = {x.text:x.attrs["data-href"].replace("//","") for x in soup.find("div", attrs={"id": "manufacturer-resources"}).find_all("a")}

    # Dimensions and Measurements

    for a,b in enumerate(soup.find("div", attrs={"id": "product-specs"}).find_all("h4", attrs={"class": "mt4"})):
        prodDataSet[b.text] = {x.find("div", attrs={"class": "specs-key"}).text : x.find("div", attrs={"class": "specs-value"}).text for x in
                           soup.find("div", attrs={"id": "product-specs"}).find_all("div", attrs={"class": "mt2"})[
                               a].find_all("div", attrs={"class": "striped--grey-light"})}
    # attribArr = {}
    # for y in dimJSON:
    #     for z in dimJSON[y]:
    #         attribArr[z] = dimJSON[y][z]
    # prodDataSet["dimJSON"] = attribArr

    return prodDataSet


def csvBuiler(products):
    headers = ['URL', 'title', 'images', 'price', 'salePrice', 'model', 'collectName', 'finish', 'overviewRAW', 'overviewText', 'manuRes', 'dimJSON']
    rows = []
    for x in products:
        rowData = []
        rowData.append(products[x]['URL'])
        rowData.append(products[x]['title'])
        rowData.append("\n".join(products[x]['images']))
        rowData.append(products[x]['price'])
        rowData.append(products[x]['salePrice'])
        rowData.append(products[x]['model'])
        rowData.append(products[x]['collectName'])
        rowData.append(products[x]['finish'])
        rowData.append(products[x]['overviewRAW'])
        rowData.append(products[x]['overviewText'])

        filesCell = ""
        for y in products[x]['manuRes']:
            filesCell += f"{y}\t:\t{products[x]['manuRes'][y]}\n"
        rowData.append(filesCell)
        for y in ['Dimensions and Measurements', 'Included Components', 'Characteristics and Features', 'Manufacturer Technology', 'Warranty and Product Information']:
            newCell = ""
            for z in products[x]['dimJSON'][y]:
                newCell += f"{z}\t:\t{products[x]['dimJSON'][y][z]}\n"
            rowData.append(newCell)
        rows.append(rowData)

def dedup(inArr):
    res = []
    for i in inArr:
        if i not in res:
            res.append(i)
    return res


def csvWrite(finalData, categID):
    with open(f"Faucets Categ-{categID} Data.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(finalData)





if __name__ == '__main__':
    with open("categIDs.txt","r") as categFile:
        categIDs = categFile.read().split("\n")


    with open("curlData.txt","r") as fileCurl:
        curlData = fileCurl.read()

    for categID in categIDs:
        if len(categID) > 2:
            totalPageCount = numberOfPages(categID, curlData)
            urls = []
            #TODO for pageNum in range(1,totalPageCount)[:2]:
            for pageNum in range(1,totalPageCount):
                urls += searchPageData(str(pageNum), categID)
            # url = 'https://www.faucet.com/delta-9159-dst-black-stainless-trinsic-pull-down-kitchen-faucet-with-magnetic
            # -docking-spray-head-includes-lifetime-warranty/f3654345'

            products = {}
            #TODO for url in urls[:5]:
            for url in urls:
                atmpt = 0
                while atmpt < 5:
                    try:
                        products[url.split("/")[-1]] = prodData(url)
                        break
                    except Exception as e:
                        atmpt += 1
                        print("Reattempt ",url ,e)


            with open(f"Faucets Categ-{categID} Data.json" , "w") as file:
                json.dump(products, file, indent=3)

            mainheaders = []
            subheaders = []
            for x in products:
                for y in products[x]:
                    if type(products[x][y]) is dict:
                        for z in products[x][y]:
                            subheaders.append(y+"\n"+z)
                    else:
                        mainheaders.append(y)
            mainheaders = dedup(mainheaders)
            subheaders = sorted(list(set(subheaders)))
            headers = mainheaders + subheaders

            bodyData = []
            for a in products:
                rowData = []
                for x in headers:
                    if "\n" in x:
                        try:
                            rowData.append(products[a][x.split("\n")[0]][x.split("\n")[1]])
                        except:
                            rowData.append("")
                    else:
                        rowData.append(products[a][x])
                bodyData.append(rowData)

            finalData = [headers] + bodyData

            csvWrite(finalData, categID)
