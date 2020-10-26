from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import json
import re
import csv
import random

# headers 是为了添加用户代理，请于此处使用(chrome://version) 更改你的抬头
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
# urls 是针对前120位 bar的三个网站所储存的list
urls = ['https://www.tripadvisor.com/Restaurants-g308272-oa{}-zfg11776-Shanghai.html#BAR_LIST'.format(str(i)) for i in
        range(0, 100, 30)]
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'


# 获取前120bar所在的TripAdvisor URL,便于下一步抓取
def get_bar_url_list(urls):
    bars_url = []
    for singe_url in urls:

        r = requests.get(singe_url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        for d in soup.findAll(id="component_2"):
            soup2 = BeautifulSoup(str(d), 'html.parser')
            for d2 in soup2.find_all(name='a', attrs={"href": re.compile(r'Restaurant_Review')}):
                if "#REVIEWS" in d2['href'] or d2['href'] in bars_url:
                    pass
                else:
                    bars_url.append('https://www.tripadvisor.com/' + d2['href'])
    bars_url = list(dict.fromkeys(bars_url))
    return bars_url


# 通过特定URL，获取未经过处理的数据集
def raw_database(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    database_1 = soup.find('script', type='application/ld+json')
    dict = json.loads(database_1.string)
    database_2 = soup.find('a', attrs={'href': re.compile('[+]86')})
    try:
        tel = database_2['href'][4:]
    except:
        tel = ""
    return dict, tel


# 清理数据集内无关数据，并展开子内容项
def dict_cleaning(dict, tel):
    dict.pop('@context')
    dict.pop('image')
    try:
        dict.pop('priceRange')
    except:
        pass
    try:
        address_dict = dict.pop('address')
    except:
        dict['Country'] = address_dict['addressCountry']['name']
        dict['addressRegion'] = address_dict['addressRegion']
        dict['addressLocality'] = address_dict['addressLocality']
        dict['postalCode'] = address_dict['postalCode']
        dict['streetAddress'] = address_dict['streetAddress']
    try:
        aggregateRating_dict = dict.pop('aggregateRating')
        dict['ratingValue'] = aggregateRating_dict['ratingValue']
        dict['reviewCount'] = aggregateRating_dict['reviewCount']
    except:
        pass
    dict['telphoneNumber'] = tel
    return dict


# 将数据写入.csv
def to_csv(list, output_CSV):
    with open(output_CSV, 'w') as f:
        w = csv.writer(f)
        for row in list:
            w.writerow(row.values())


# 将数据抬头写入
def init_csv(output_CSV):
    with open(output_CSV, 'w') as f:
        w = csv.writer(f)
        w.writerow(['type', 'name', 'url', 'Country', 'addressRegion', 'addressLocality', 'postalCode', 'streetAddress',
                    'ratingValue', 'reviewCount', 'telphoneNumber'])


# 完整封装所有步骤
def DataCollection(urls, filename):
    bars_url_list = get_bar_url_list(urls)
    print("step1: Get all urls of bars")
    dictionary_list = []
    init_csv(filename)
    n = 1
    for single_url in bars_url_list:
        ran = random.randint(5, 10)
        time.sleep(ran)
        raw_dict, tel = raw_database(single_url)
        dict = dict_cleaning(raw_dict, tel)
        dictionary_list.append(dict)
        print(n, "line finished")
        if n == 100:
            to_csv(dictionary_list, filename)
            break
        elif n / 20 == 0:
            to_csv(dictionary_list, filename)
            dictionary_list = []
        else:
            pass
        n = n + 1


# 运行结果
DataCollection(urls, 'Travel_Advsior_Bars.csv')

# 我之前对于爬虫了解不深，是通过这三天加强理解后做出来的。因此在算法复杂度上可能不完善，期待后续更改。
# header 请填写您chrome浏览器的 用户代理 (chrome://version)，换头 增加爬取可靠性
# 加入time.sleep, header 并随机休整时间是因为tripadvisor 的反爬虫机制，尽可能避免被反
