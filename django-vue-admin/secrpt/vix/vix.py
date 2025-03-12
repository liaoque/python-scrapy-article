import time
from os.path import dirname
from time import sleep

import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import sys
import sqlite3
import vixdb
from common import dingding

# VIX计算函数
def calculate_vix(option_df_near, option_df_next, r, T1_days, T2_days):
    T1 = T1_days / 365
    T2 = T2_days / 365
    T30 = 30 / 365

    # 第一步: 计算远期价格F
    def forward_price(df, r, T):
        df['diff'] = np.abs(df['call'] - df['put'])
        K0_row = df.loc[df['diff'].idxmin()]
        K0 = K0_row['K']
        F = K0 + np.exp(r * T) * (K0_row['call'] - K0_row['put'])
        return F, K0

    F1, K0_1 = forward_price(option_df_near, r, T1)
    F2, K0_2 = forward_price(option_df_next, r, T2)

    # 第二步: 计算方差sigma^2
    def variance(df, F, K0, r, T):
        df = df.copy()
        df.loc[df.index[0], 'delta_K'] = df['K'].iloc[1] - df['K'].iloc[0]
        df.loc[df.index[-1], 'delta_K'] = df['K'].iloc[-1] - df['K'].iloc[-2]
        df.loc[df.index[1:-1], 'delta_K'] = (df['K'].iloc[2:].values - df['K'].iloc[:-2].values) / 2

        df['Q'] = np.where(df['K'] < K0, df['put'], np.where(df['K'] > K0, df['call'], (df['call'] + df['put']) / 2))

        term = df['delta_K'] / (df['K'] ** 2) * np.exp(r * T) * df['Q']
        sigma_sq = (2 / T) * term.sum() - (1 / T) * ((F / K0 - 1) ** 2)

        return sigma_sq

    sigma1_sq = variance(option_df_near, F1, K0_1, r, T1)
    sigma2_sq = variance(option_df_next, F2, K0_2, r, T2)

    # 第三步: 插值得到30天方差
    sigma30_sq = ((T2 - T30) / (T2 - T1)) * sigma1_sq + ((T30 - T1) / (T2 - T1)) * sigma2_sq

    # 第四步: 计算VIX
    VIX = 100 * np.sqrt(sigma30_sq)

    return VIX

def get_gz_rate():
    url = 'http://datacenter-web.eastmoney.com/api/data/v1/get?callback=&reportName=RPTA_WEB_TREASURYYIELD&columns=ALL&sortColumns=SOLAR_DATE&sortTypes=-1&token=&pageNumber=1&pageSize=1&_='
    response = requests.get(url)
    return response.json()

def get_etf_qq_list_date(code):
    url = 'http://push2.eastmoney.com/api/qt/stock/get'
    params = {
        'cb': '',
        'ut': '',
        'mspt': 1,
        '_': '',
        'secid': code
    }
    response = requests.get(url, params=params)
    return response.json()

def get_etf_qq_list(code, date):
    url = 'http://push2.eastmoney.com/api/qt/slist/get'
    params = {
        'np': 1,
        'fltt': 1,
        'invt': 2,
        'spt': 9,
        'cb': '',
        'fields': 'f12,f13,f14,f1,f2,f4,f334,f330,f3,f152,f108,f5,f249,f250,f161,f340,f339,f341,f342,f343,f345,f344,f346,f347',
        'fid': 'f161',
        'pn': 1,
        'pz': 100,
        'dect': 1,
        'po': 0,
        'secid': code,
        'exti': date
    }
    response = requests.get(url, params=params)
    return response.json()

def getQq(code, date_str, dateStrNext, r):
    etf300_date = get_etf_qq_list_date(code)
    etf300 = get_etf_qq_list(code, date_str)
    etf300_next = get_etf_qq_list(code, dateStrNext)
    option_df_near = pd.DataFrame({
        'K':  [ item['f161'] for item in etf300['data']['diff']],
        'call':  [ item['f2'] / 1000 for item in etf300['data']['diff']],
        'put':  [ item['f341'] / 1000 for item in etf300['data']['diff']],
    })

    option_df_next = pd.DataFrame({
        'K': [item['f161'] for item in etf300_next['data']['diff']],
        'call': [item['f2'] / 1000 for item in etf300_next['data']['diff']],
        'put': [item['f341'] / 1000 for item in etf300_next['data']['diff']],
    })

    etf300_vix = calculate_vix(
        option_df_near,
        option_df_next,
        r,
       etf300_date['data']['optionExpireInfo'][0]['days'],
       etf300_date['data']['optionExpireInfo'][1]['days'])
    return etf300_vix

d = datetime.now()
date_str = d.strftime('%Y%m')
next_month = (d + timedelta(days=32)).replace(day=1)
date_str_next = next_month.strftime('%Y%m')

res =  get_gz_rate()
r = res['result']['data'][0]['EMM00588704']




current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)


def getQqForDb(cursor, code):
    etf300_vix = getQq(code, date_str, date_str_next, r)
    row = vixdb.query(cursor, d.strftime('%Y%m%d'), code)
    if row:
        vixdb.update(cursor, row['id'], etf300_vix)
    else:
        vixdb.insert(cursor, code, d.strftime('%Y%m%d'), etf300_vix)

    if time.strftime("%H") in [ '09', '12', '15']:
        dingding.dingding(d.strftime('%Y%m%d') + "----"+code + ";vix;"+str(round(etf300_vix, 3)))
        sleep(1)
    return etf300_vix


def compute():
    dbname = dirname(dirname(dirname(__file__))) + "/backend/vix.db"
    conn = sqlite3.connect(dbname)
    conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    cursor = conn.cursor()

    vixdb.init(cursor)

    getQqForDb(cursor,'1.510300')
    getQqForDb(cursor, '1.510050')
    getQqForDb(cursor, '1.510500')
    getQqForDb(cursor,'1.588000')

    conn.commit()

    cursor.close()
    conn.close()



if __name__ == "__main__":
    compute()