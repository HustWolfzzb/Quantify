import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_content(url = 'http://www.chinanews.com/auto/2019/01-30/8743035.shtml'):

    res = requests.get(url)
    # res.encoding='GBK'  # html: ISO-8859-1 (2012)
    res.encoding = 'utf-8' # (2019)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.find('h1')
    print(title.text.strip())
    news_contents = ''
    contents = soup.find('div', 'left_zw').find_all('p')
    for content in contents:
        if 'function' in content.text:
            continue
        news_contents = news_contents + content.text.strip()
    print(news_contents)


def get_news_table(date):
    url = 'http://www.chinanews.com/scroll-news/' + date +'/news.shtml'
    res = requests.get(url)
    # res.encoding='GBK'  # html: ISO-8859-1 (2012)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    li_tag = soup.find('div','content_list').find_all('li')
    category_list = []
    title_list = []
    url_list = []
    for li in li_tag:
        try:
            info = li.find_all('a')
            category = info[0].text
            if category in ['滚动', '要闻', '时政', '国际', '社会', '军事', '港澳', '台湾', '财经', '金融', '房产', '汽车', '能源', 'IT']:
                category_list.append(category)
                news_title = info[1].text
                title_list.append(news_title)
                news_url = 'http://www.chinanews.com'+str(info[1].get('href'))
                url_list.append(news_url)
                print("have done!"+ news_title+":"+news_url)
        except:
            continue
    c = {'类别':category_list,
        '标题':title_list,
        'url':url_list
    }
    data=pd.DataFrame(c)
    return data


if __name__ == '__main__':
    get_news_table('2021/0518')