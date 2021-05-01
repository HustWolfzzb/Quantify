from Feature.feature import RSI,Momentum
import numpy as np
import tushare as ts
ts.set_token('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')

def process_data(ts_code='600031.SH', start_date='20140101', end_date='20210101', ma=[5, 20, 50], adj='qfq', type='C'):
    data = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, ma=ma, adj=adj)
    data = data[::-1].reset_index()
    data['delta_ma5'] = (data['close'] - data['ma5'] ) / data['close']
    data['delta_ma20'] = (data['close'] - data['ma20'] )/ data['close']
    data['delta_ma50'] = (data['close'] - data['ma50'] )/ data['close']
    for i in range(len(data)):
        for j in [5, 15, 30]:
            data.loc[i, 'mo{}'.format(j)] = Momentum(data, 'close', i, j)
    data['vol_chg'] = 0
    for i in range(1, len(data)):
        data.loc[i,'vol_chg'] = ( data.loc[i,'vol'] - data.loc[i - 1,'vol'] ) / data.loc[i,'vol']
    data['delta_ma_v_5'] = (data['vol'] - data['ma_v_5'] ) / data['vol']
    data['delta_ma_v_20'] = (data['vol'] - data['ma_v_20']) / data['vol']
    data['delta_ma_v_50'] = (data['vol'] - data['ma_v_50']) / data['vol']
    data['zhangdie'] = np.where(data.change > 0, 1, 0)
    data['RSI-7'] = -1
    data['RSI-21'] = -1
    data['RSI-49'] = -1
    need_col = [ 'pct_chg', 'delta_ma5', 'delta_ma20',
           'delta_ma50', 'delta_ma_v_5', 'delta_ma_v_20', 'delta_ma_v_50',
           'RSI-7', 'RSI-21', 'RSI-49', 'vol_chg', 'mo5', 'mo15', 'mo30']
    if type!='C':
        need_col.append('close')
    for i in range(len(data)):
        for j in [7,21,49]:
            data.loc[i,'RSI-{}'.format(j)] = RSI(data, 'change', i, j)
    data = data.iloc[49:,:]
    data.set_index(['trade_date'], inplace=True)
    X = data[need_col]
    if type=='C':
        y_cls = data.zhangdie
    else:
        y_cls = data.change
    return X, y_cls

