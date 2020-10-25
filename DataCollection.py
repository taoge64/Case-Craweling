from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import json
import re
pd.set_option('max_rows',100)
headers = {  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
urls = ['https://www.tripadvisor.com/Restaurants-g308272-oa{}-zfg11776-Shanghai.html#BAR_LIST'.format(str(i)) for i in range(0,100,30)]

def get_bar_url_list(urls):
    bars_url = []
    for singe_url in urls:
        r = requests.get(singe_url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        for d in soup.findAll(id="component_2"):
            soup2 =BeautifulSoup(str(d),'html.parser')
            for d2 in soup2.find_all(name='a',attrs={"href":re.compile(r'Restaurant_Review')}):
                if "#REVIEWS" in d2['href'] or d2['href'] in bars_url:
                    pass
                else:
                    bars_url.append('https://www.tripadvisor.com/'+d2['href'])
    return  bars_url

def get_bar_data(bar_url_list):
    for single_bar_url in bar_url_list:
        r = requests.get(single_bar_url, headers=headers)
        soup =  BeautifulSoup(r.text, 'html.parser')
        title = soup.title
        print(title)
bar_url_list = get_bar_url_list(urls)
get_bar_data(bar_url_list)



print(len(get_bar_url_list(urls)))

#test = pd.DataFrame(columns=name, data=dataset[2])

