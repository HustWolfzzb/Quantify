# Quantify
情绪指标

## 数据来源

###### 文本数据
新闻快讯来自Tushare的pro.news API,来源比较丰富，而且内容很多的说，

###### 词性数据
金融市场的词性表,来自[李峰教授 Bian et al. (2019) ](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3446388)
训练的中文财经类的[Sentiment词典列表(https://github.com/seanxlwang/Bianetal2019CFSD)。
该列表附在他们文章的最后是pdf形式。这里把它整理成EXCEL形式，方便使用。

The sentiment variable equals to 1 if word is positive, and -1 if negative

## 情绪分析方案

###### 目前是个简单的词性叠加，正面词多就好，否则坏。

###### 后续准备引入神经网络的情绪分析，做一个更好的二分类器。

