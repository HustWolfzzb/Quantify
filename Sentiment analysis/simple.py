import pandas as pd
from DataEngine.Data import get_news
import jieba

pos_neg_word = pd.read_excel('/Users/zhangzhaobo/PycharmProjects/Quantify/Sentiment analysis/Li_CFSD_list.xlsx')
pos_word = []
neg_word = []
for x in range(len(pos_neg_word)):
    if pos_neg_word.iloc[x]['sentiment'] == 1:
        pos_word.append(pos_neg_word.iloc[x]['word'])
    else:
        neg_word.append(pos_neg_word.iloc[x]['word'])
newsdata = get_news()


def pos_senti(content):
    """
    content: 待分析文本内容
    返回正面词占文本总词语数的比例
    """
    try:
        pos_word_num = 0
        words = jieba.lcut(content)
        for kw in pos_word:
            pos_word_num += words.count(kw)
        return pos_word_num/len(words)
    except:
         return 0

def neg_senti(content):
    """
    content: 待分析文本内容
    返回负面词占文本总词语数的比例
    """
    try:
        neg_word_num = 0
        words = jieba.lcut(content)
        for kw in neg_word:
            neg_word_num += words.count(kw)
        return neg_word_num/len(words)
    except:
        return 0

newsdata['pos']=newsdata['content'].agg(pos_senti)
newsdata['neg']=newsdata['content'].agg(neg_senti)
print(newsdata.head(10))

