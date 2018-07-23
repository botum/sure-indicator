"""
Support and resistance finder from dataframe with OHLC data
author@: Bruno Sarlo
github@: https://github.com/botum/sure-indicator
"""
import numpy as np
import pandas as pd
from datetime import datetime

from technical.util import *

from sklearn.cluster import MeanShift, estimate_bandwidth

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_pivots(df, su, re, interval: str='no_interval', pair: str='no_pair', filename: str=None):
    plt.figure(num=0, figsize=(20,10))
    df['old_date'] = df['date']
    to_datetime(df['date'])
    df.set_index(['date'],inplace=True)
    plt.plot(df.high, 'r', alpha=0.5)
    plt.plot(df.close, 'k', alpha=0.5)
    plt.plot(df.low, 'g', alpha=0.5)

    # plt.plot(df.bb_lowerband, 'b', alpha=0.5, linewidth=2)
    # plt.plot(df.bb_upperband, 'b', alpha=0.5, linewidth=2)

    for r in re:
        plt.axhline(y=r, color='r', alpha=0.5, linewidth=1)
    for s in su:
        plt.axhline(y=s, color='g', alpha=0.5, linewidth=1)

    plt.xlim(df.index[0], df.index[-1])
    plt.ylim(df.low.min()*0.99, df.high.max()*1.01)
    plt.xticks(rotation='vertical')

    if not filename:
        filename = 'chart_plots/sure_' + pair.replace('/', '-') + '-' +  interval +  datetime.utcnow().strftime('-%M') + '.png'

    plt.scatter(df.index, df.r1, color='r', s=3)
    plt.scatter(df.index, df.s1, color='g', s=3)

    plt.savefig(filename)
    plt.close()
    df['date'] = df['old_date']


def in_range(x, target, percent):
    start = target - target * percent
    end = target + target * percent
    check = (start <= x) & (end >= x)
    # print (check)
    return check

# we need serie script to get sure on indicators too.
# def get_sure(serie: pd.Series, pair: str, interval: int=1, piv_type: str='piv', full_df: pd.DataFrame=None) -> pd.DataFrame:

def get_cluster(df, cols, quantile, samples):

    # clustered points
    data = df.as_matrix(columns=cols)
    try:
        bandwidth = estimate_bandwidth(data, quantile=quantile, n_samples=samples)
        ms1 = MeanShift(bandwidth=bandwidth, bin_seeding=True)
        ms1.fit(data)
    except Exception as ex:
        print('Unexpected error when analyzing ticker pivots', str(ex))
        return []

    pivots = []

    # print ('labels', ms1.labels_)
    for k in range(len(np.unique(ms1.labels_))):
            my_members = ms1.labels_ == k
            values = data[my_members, 0]
            # print (values)

            # find the edges
            if len(values) > 0:
                pivots.append(min(values))
                pivots.append(max(values))

    pivots = sorted(pivots)
    return pivots


def get_sure_OHLC(self, df: pd.DataFrame, intervals: list, n: int=2,
                quantile: int= 0.05, samples: int=None,
                up_thresh: int=0.02, down_thresh: int=0.02) -> pd.DataFrame:

    if samples == None:
        samples = len(df)

    # # custom settings if we're getting one or another.
    # if piv_type == 'sup':
    #     quantile = 0.01
    #     cols = ['low', 'high']
    #     gap = 1.05
    #     interval = 1
    # elif piv_type == 'res':
    #     quantile = 0.01
    #     cols = ['high', 'low']
    #     gap = 0.96
    #     interval = 1
    #
    # if len(full_df) <= len(df):
    #     full_df = df
    # print ('len df: ', len(df))
    # print ('len full_df: ', len(full_df))

    # print(len(df) * quantile)
    # if full_df.empty:
    #     logger.warning('Empty dataframe for pair %s', pair)
    #     return []  # return False ?
    # elif not len(df) * quantile > 1:
    #     print('dataframe too short: ', len(df))
    #     samples = len(df) * 0.1

    su = get_cluster(df, ['high', 'low'], quantile, samples)
    su_gap = [su[0]]
    for i in range(1, len(su)):
        if su[i] <= (su_gap[-1] * (1 + down_thresh)):
            su_gap.append(su[i])
    su = np.array(su_gap)

    re = sorted(get_cluster(df, ['high', 'low'], quantile, samples), reverse=True)
    re_gap = [re[0]]
    for i in range(1, len(re)):
        if re[i] <= (re_gap[-1] * (1 - up_thresh)):
            re_gap.append(re[i])
    re = np.array(re_gap)

    for i in intervals:
        def set_sure(row):
            s1 = None
            r1 = None
            # print (i)
            # su = []
            # re = []
            # # candle coincidences
            # body = []
            # for p in pivots:
            #     if row.low >= p:
            #         su.append(p)
            #     elif row.high <= p and len(re) < n:
            #         re.append(p)
            #     else:
            #         body.append(p)
            # return Series({"s1": su[-1], "s2": su[-1],
            #                 "r1": re[0], "r2": re[0],
            #                 "body": body })
            #
            # print(pivots[np.max(np.where(row.low >= pivots))])
            # sure = pd.Series({"s1": '', "r1": '', "body": ''})
            try:
                s1 = np.max(su[np.where(row.low >= su)])
            except ValueError:  #raised if `where` is empty.
                pass
            try:
                r1 = np.min(re[np.where(row.high <= re)])
            except ValueError:  #raised if `where` is empty.
                pass
            # try:
            #     body_indexes = np.where(row.high > pivots & row.low < pivots)
            #     sure.body = pivots[np.mean()]
            # except ValueError:  #raised if `where` is empty.
            #     pass
            # print ('sure: ', type(sure))
            return pd.Series([s1, r1])

        df[['s1','r1']] = df.apply(set_sure, axis=1)
            #
            # def set_sup(row):
            #     supports = sorted(piv_clean['sup'], reverse=True)
            #     for sup in supports:
            #         if row["low"] >= sup:
            #             return sup
            # def set_sup2(row):
            #     supports = sorted(piv_clean['sup'], reverse=True)
            #     for sup in supports:
            #         if row["low"] >= sup and sup < row['s1'] :
            #             return sup
            # df = df.assign(s1=df.apply(set_sup, axis=1))
            # df = df.assign(s2=df.apply(set_sup2, axis=1))
            #
            # # create resistances
            #
            # for i in range(1, len(pivots)):
            #     if pivots[i] <= (resistances[-1] * gap):
            #         resistances.append(pivots[i])
            # piv_clean['res'] = resistances
            # def set_res(row):
            #     res = sorted(piv_clean['res'])
            #     for r in res:
            #         if row["high"] <= r and r >= row["s1"] * 1.02:
            #             return r
            # def set_res2(row):
            #     res = sorted(piv_clean['res'])
            #     for r in res:
            #         if row["high"] <= r and row["r1"] < r and r >= row["s1"] * 1.02:
            #             return r
            # df = df.assign(r1=df.apply(set_res, axis=1))
            # df = df.assign(r2=df.apply(set_res2, axis=1))

    # print (df)
    return df, su, re
