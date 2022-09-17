#Momentum Strategy

import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings;warnings.simplefilter('ignore')
import pandas as pd
import numpy as np
import tushare as ts
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数
import datetime
import time
from time import strftime
#数据准备
code = 'hs300'
end_day = time.strftime("%Y-%m-%d",time.localtime())
data=ts.get_k_data(code,start='2018-01-01',end= end_day)[['date','close']]
data.rename(columns={'close':'price'},inplace = True)
data.set_index('date',inplace = True)
#策略思路
data['returns'] = np.log(data['price']/data['price'].shift(1))
data['position'] = np.sign(data['returns'])
#计算收益率
data['strategy'] = data['position'].shift(1) * data['returns']
#data[['returns','strategy']].cumsum().apply(np.exp).plot(figsize=(16,9))
data['strategy_total'] = data['strategy'].dropna().cumsum().apply(np.exp)

#避免频繁买卖开仓
#策略优化思路——参数优化穷举
data['position_10'] = np.sign(data['returns'].rolling(10, min_periods=1).mean())
data['strategy_10'] = data['position_10'].shift(1)*data['returns']
#data[['returns','strategy_10']].dropna().cumsum().apply(np.exp).plot(figsize=(16,9))

#寻找最优参数 离散return计算方法
data['returns_dis'] = data['price'] / data['price'].shift(1)-1
#data['returns_dis'] = data['price'].pct_change()
data['returns_dis_cum'] = (data['returns_dis']+1).cumprod()

price_plot  = ['returns_dis_cum'] 
for days in range(10,200,2):
    price_plot.append('%d Day' % days)
    data['position_%dd' % days] = np.where(data['returns'].rolling(days).mean()>0, 1, -1)
    #data['position_%d' % days] = np.sign(data['returns'].rolling(days).mean())
    data['strategy_%dd' % days] = data['position_%dd' % days].shift(1) * data['returns']
    data['%d Day' % days] = (data['strategy_%dd' % days]+1).cumprod()
df = data[price_plot]
rtn_max = df.values[-1].max()
l=df.idxmax(axis=1)
data[price_plot].dropna().plot(title=f'{code} Multi Parameters Momentum Strategy',figsize=(50,25), style=['--', '--', '--', '--','--', '--','--'])

print(f'\n*******************\n策略结果\n\n累计收益： {rtn_max.round(3)} \n------------------ \n策略均线:  {l[-1]}\n\n*******************')

