import pandas as pd 
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from sklearn.preprocessing import MinMaxScaler
import datetime

def dTimeWarp(dat1,dat2,col,data,c,e):
  dat1 = datetime.datetime.strptime(dat1, '%Y-%m-%d')
  dat2 = datetime.datetime.strptime(dat2, '%Y-%m-%d')
  d1 = data['Date'].loc[lambda x: x==dat1].index
  while len(d1) < 1:
    dat1 += datetime.timedelta(days=1)
    d1 = data['Date'].loc[lambda x: x==dat1].index
  d2 = data['Date'].loc[lambda x: x==dat2].index
  while len(d2) < 1:
    dat2 += datetime.timedelta(days=1)
    d2 = data['Date'].loc[lambda x: x==dat2].index
  e = e.loc[e.asset_1 == col]['asset_2']
  c = c[e]
  
  ft = c.iloc[d1[0]:d2[0]]
  dt = {}
  k = data[col]
  k = k.iloc[d1[0]:d2[0]]
  for j in ft:
    dt[(col,j)],p = fastdtw(k,ft[j])
        
  values = dt.values()
  min_ = min(values)
  max_ = max(values)

  normalized_dt = {key: 1 - ((v - min_ ) / (max_ - min_) )  for (key, v) in dt.items()}
  f = [(j,normalized_dt[(i,j)]) for i,j in normalized_dt]
  f.sort(key=lambda x: x[1],reverse = True)
  return f