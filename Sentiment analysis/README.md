# Quantify
情绪指标

# 数据来源

### 文本数据
新闻快讯来自Tushare的pro.news API,来源比较丰富，而且内容很多的说，

### 词性数据
金融市场的词性表,来自[李峰教授 Bian et al. (2019) ](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3446388)
训练的中文财经类的[Sentiment词典列表(https://github.com/seanxlwang/Bianetal2019CFSD)。
该列表附在他们文章的最后是pdf形式。这里把它整理成EXCEL形式，方便使用。

The sentiment variable equals to 1 if word is positive, and -1 if negative

# 情绪分析方案

## 简单的词性叠加

通过结合金融学的特征工程，然后对文本做统计学分析，正面词多就好，否则坏。

具体内容见simple.py

## 引入SVM和LSTM神经网络的情绪分析

#### 环境要求
- Unix/Linux系统
- python 2.7
- python包安装： keras,sklearn,gensim,jieba,h5py,numpy,pandas
```
sudo pip install -r requirements.txt
```
#### 用法

###### 使用SVM分类器进行情感分类：
```
python predict.py svm 这个手机质量很好，我很喜欢，不错不错

```
```
python predict.py svm 这书的印刷质量的太差了吧，还有缺页，以后再也不买了

```

##### 使用LSTM进行情感分类：
```
python predict.py lstm 酒店的环境不错，空间挺大的
```
```
python predict.py lstm 电脑散热太差，偶尔还蓝屏，送货也太慢了吧
```
#### 程序
- Sentiment_lstm.py 使用word2vec和LSTM训练和预测
- Sentiment_svm.py  使用word2vec和svm训练和预测
- predict.py  调用Sentiment_lstm.py及Sentiment_svm.py进行预测

#### 数据
- ./data/ 原始数据文件夹
  - data/neg.xls 负样本原始数据
  - data/pos.xls 正样本原始数据

- ./svm_data/ svm数据文件夹
  - ./svm_data/\*.npy 处理后的训练数据和测试数据
  - ./svm_data/svm_model/ 保存训练好的svm模型
  - ./svm_data/w2v_model/ 保存训练好的word2vec模型


- ./lstm_data/ lstm数据文件夹
  - ./lstm_data/Word2vec_model.pkl 保存训练好的word2vec模型
  - ./lstm_data/lstm.yml  保存训练网络的结构
  - ./lstm_data/lstm.h5  保存网络训练到的权重
  
#### 详细介绍

[购物评论情感分析的实现](http://buptldy.github.io/2016/07/20/2016-07-20-sentiment%20analysis/)

