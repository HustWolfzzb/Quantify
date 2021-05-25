import random
import os
import time
from Feature.pre_process_data import process_data
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def sumi():
    date = np.linspace(1,30,30)
    beginPrice = np.array([2923.19,2928.06,2943.92,2946.26,2944.40,2920.85,2861.33,2854.58,2776.69,2789.02,
                           2784.18,2805.59,2781.98,2798.05,2824.49,2762.34,2817.57,2835.52,2879.08,2875.47,
                           2887.66,2885.15,2851.02,2879.52,2901.63,2896.00,2907.38,2886.94,2925.94,2927.75])
    endPrice = np.array([2937.36,2944.54,2941.01,2952.34,2932.51,2908.77,2867.84,2821.50,2777.56,2768.68,
                         2794.55,2774.75,2814.99,2797.26,2808.91,2815.80,2823.82,2883.10,2880.00,2880.33,
                         2883.44,2897.43,2863.57,2902.19,2893.76,2890.92,2886.24,2924.11,2930.15,2957.41])


    for i in range(0,30):  # 画柱状图
        dateOne = np.zeros([2])
        dateOne[0] = i
        dateOne[1] = i
        priceOne = np.zeros([2])
        priceOne[0] = beginPrice[i]
        priceOne[1] = endPrice[i]
        if endPrice[i]>beginPrice[i]:
            plt.plot(dateOne,priceOne,'r',lw=6)
        else:
            plt.plot(dateOne,priceOne,'g',lw=6)
    plt.xlabel("date")
    plt.ylabel("price")

    dateNormal = np.zeros([30,1])
    priceNormal = np.zeros([30,1])
    #归一化
    for i in range(0,30):
        dateNormal[i,0] = i/29.0
        priceNormal[i,0] = endPrice[i]/3000.0
    return dateNormal, priceNormal


X_origin, Y_origin = process_data(type='C')
Y = Y_origin.shift(-1).fillna(0)
trainLength = int(len(X_origin) * 0.8)
X = X_origin.iloc[:trainLength, :]
Y = Y[:trainLength]
X_test = X_origin.iloc[trainLength:, :]
Y_test = Y[trainLength:]
# X = X_origin.iloc[:len(X_origin)-1, :]
# Y = Y[:len(Y)-1]


def get_batch(batch_size=100):
    loc = []
    for i in range(batch_size):
        loc.append(random.randint(0,len(X)-1))
    X_re = []
    y_re = []
    for i in loc:
        X_re.append(X.iloc[i,:].tolist())
        y_re.append(Y[i])
    return np.array(X_re), np.array(y_re)

features_num = len(X.columns)

x = tf.placeholder(tf.float32, [None, features_num])
y = tf.placeholder(tf.float32, [None, 1])
# X->hidden_layer
w1 = tf.Variable(tf.random_uniform([features_num, 25], 0, 1))
b1 = tf.Variable(tf.random_uniform([25],0,1))
out_put_hidden1 = tf.matmul(x,w1)+b1
# layer1 = tf.nn.sigmoid(out_put_hidden1) # 激励函数
# # hidden_layer->output
# w2 = tf.Variable(tf.random_uniform([25,1],0,1))
# b2 = tf.Variable(tf.random_uniform([1],0,1))
# output = tf.matmul(layer1, w2) + b2
# # down = tf.reshape(y - output, [-1,1])
# layer2 = tf.nn.relu(output)
# layer2 = y-output
loss = tf.reduce_sum(tf.square(out_put_hidden1 - y)) #y为真实数据， layer2为网络预测结果
# loss1 = tf.reduce_sum(loss, 1, keep_dims=False)

def run():
    #梯度下降
    train_op = tf.train.GradientDescentOptimizer(0.1).minimize(loss)
    with tf.Session() as sess:
        start = time.clock()
        sess.run(tf.global_variables_initializer())
        for i in range(0,20000):
            XX, YY = get_batch(100)
            YY=np.expand_dims(YY,1)
            # XX, YY = sumi()
            # print(XX.shape)
            # print(YY.shape)
            loss_r = sess.run(loss,feed_dict={x:XX,y:YY})
            if i % 200 ==0 :
                print("Loss:%s, Time:%s "%(loss_r, round(time.clock() - start, 2)), )
            if loss_r < 1:
                break
        #预测， X  w1w2 b1b2 -->layer2
        # pred = sess.run(output, feed_dict={x:X_test})
        # print(pred)
        # predPrice = np.zeros([30,1])
        # for i in range(0,30):
        #     predPrice[i,0]=(pred*3000)[i,0]
        # plt.plot(date,predPrice,'b',lw=1)

run()
# plt.show()
