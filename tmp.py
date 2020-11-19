import re

import requests
curlData = """
curl 'https://www.faucet.com/app/api/search/products?r=48&s=SCORE&p=2&categoryId=80010&lastSearchPage=%252Fkitchen-faucets%252Fc80010%253Fr%253D48%2526s%253DSCORE%2526p%253D2%2526categoryId%253D80010' \
  -H 'authority: www.faucet.com' \
  -H 'pragma: no-cache' \
  -H 'cache-control: no-cache' \
  -H 'accept: */*' \
  -H 'dnt: 1' \
  -H 'x-requested-with: XMLHttpRequest' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://www.faucet.com/kitchen-faucets/c80010?r=48&s=SCORE&p=2&categoryId=80010' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'cookie: CID=n1MNakSbF_ZHizFZDsxQ91zOn54Ap4na; _px_uAB=MTN8ZmFsc2U=; _px_f394gi7Fvmc43dfg_user_id=MzMxYTFjMDEtZjFjMi0xMWVhLThiMzctODEwMDEzYjVlYjY4; bv_segment=%7B%22testId%22%3A%22rh_v3_always_on%22%2C%22segment%22%3A%22rh%7Cpro_con%22%7D; _dy_c_exps=; _dycnst=dg; _pxvid=fb5017b1-108f-11eb-acb1-37e4230d72f2; _dyid=2756203299971207666; _dy_geo=IN.AS.IN_KL.IN_KL_Kochi; _dy_df_geo=India..Kochi; _dyid_server=2756203299971207666; _vz=viz_5f8b1253beec4; _dy_c_att_exps=; BVBRANDID=c2d6319d-2749-4974-b026-7db2f4992db1; _dycst=dk.l.c.ws.; LASTSEARCHPAGE=%2Fkitchen-faucets%2Fc80010%3Fr%3D48%26s%3DSCORE%26p%3D1%26categoryid%3D80010; _pxhd=9070e4b27c0543724d219dc03f9fa85a686494a00761b81b56f550d55daa7210:fb5017b1-108f-11eb-acb1-37e4230d72f2; wpn_https={"last_shown":"Thu, 05 Nov 2020 02:52:53 GMT","shown_count":1}; _dy_csc_ses=t; AMCVS_F5FA1253512D2B590A490D45%40AdobeOrg=1; AMCV_F5FA1253512D2B590A490D45%40AdobeOrg=1687686476%7CMCMID%7C59365797598020233390816865562396441040%7CMCOPTOUT-1604551974s%7CNONE%7CvVersion%7C3.0.0; s_cc=true; _dyjsession=e5633291d11982e06d1695d551e6d656; dy_fs_page=www.faucet.com%2Fkitchen-faucets%2Fc80010%3Fr%3D48%26s%3Dscore%26p%3D1%26categoryid%3D80010; _dy_ses_load_seq=32385%3A1604544787029; _dy_soct=443084.788033.1604544787; _dy_lu_ses=e5633291d11982e06d1695d551e6d656%3A1604544788112; _dy_toffset=-1; _px2=eyJ1IjoiMDg3OWUyNTAtMWYxMi0xMWViLTlkYWQtMDllODYxNDUzZjRlIiwidiI6ImZiNTAxN2IxLTEwOGYtMTFlYi1hY2IxLTM3ZTQyMzBkNzJmMiIsInQiOjE2MDQ1NDUwODkyMDAsImgiOiIxOWY0NGVjMDBjNTMzM2FkZmIxYzQ4NzVhZjlmYWVkY2EzNDEzNjk2ZTY2YTUxZGYzZjlhZWVjNzRhOTM1NjdkIn0=; _pxde=1556884edb2f252270f5cefba7d2c851efffe52233192d229fcc6f9c1eddb322:eyJ0aW1lc3RhbXAiOjE2MDQ1NDQ3OTA4ODl9; _px_5909295845_cs=eyJpZCI6IjAwZWM3MTYwLTFmMTItMTFlYi1hZTY4LWE3NGYwZDc4ZmY1MyIsInN0b3JhZ2UiOnsiTkN5WDBiS3oiOnRydWV9LCJleHBpcmF0aW9uIjoxNjA0NTQ2NjUyNzg1fQ==' \
  --compressed
"""
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
    'referer': 'https://www.faucet.com/kitchen-faucets/c80010?r=48&s=SCORE&p=2&categoryId=80010',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': re.findall(r"cookie: ([^\n]+)'", curlData)[0]
}

params = (
    ('r', '48'),
    ('s', 'SCORE'),
    ('p', '2'),
    ('categoryId', '80010'),
    ('lastSearchPage', '%2Fkitchen-faucets%2Fc80010%3Fr%3D48%26s%3DSCORE%26p%3D2%26categoryId%3D80010'),
)

response = requests.get('https://www.faucet.com/app/api/search/products', headers=headers, params=params)

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://www.faucet.com/app/api/search/products?r=48&s=SCORE&p=2&categoryId=80010&lastSearchPage=%252Fkitchen-faucets%252Fc80010%253Fr%253D48%2526s%253DSCORE%2526p%253D2%2526categoryId%253D80010', headers=headers)
out = response.json()["pagination"]['numberOfPages']
out = response.text
