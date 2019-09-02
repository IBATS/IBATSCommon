#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-4-30 上午9:36
@File    : __init__.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import os
import pandas as pd
import numpy as np
from ibats_utils.mess import str_2_date

from ibats_common import module_root_path


def load_data(file_name, encoding=None, folder_path=None, index_col=None, range_from=None, range_to=None)-> pd.DataFrame:
    if folder_path is None:
        folder_path = os.path.join(module_root_path, 'example', 'data')
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path, encoding=encoding, index_col=index_col,
                     parse_dates=[index_col] if index_col is not None else False)
    # df.index = pd.DatetimeIndex(df.index)
    # 获取指定日期区间的数据
    if range_from is not None:
        is_in_range = df.index >= range_from
    else:
        is_in_range = None
    if range_to is not None:
        is_in_range &= df.index <= range_to
    if is_in_range is not None:
        df = df[is_in_range]

    return df


def get_trade_date_series():
    df = load_data('trade_date.csv').astype('datetime64[ns]')
    # ret_list = [str_2_date(_) for _ in load_data('trade_date.csv').T.to_numpy()[0]]
    date_s = df.iloc[:, 0]
    return date_s


def get_delivery_date_series(instrument_type):
    df = load_data(
        'future_info.csv'
    ).set_index(
        'symbol'
    ).filter(
        regex='^' + instrument_type + r'(?=\d+$)', axis=0
    )
    # re_pattern_instrument_header = re.compile(r'[A-Za-z]+(?=\d+$)')
    date_s = df["delist_date"].astype('datetime64[ns]').sort_values()
    # ret_list = [str_2_date(_) for _ in load_data('trade_date.csv').T.to_numpy()[0]]
    return date_s


def _test_load_data():
    from ibats_utils.mess import is_windows_os, str_2_date
    DATA_FOLDER_PATH = r'D:\WSPych\IBATSCommon\ibats_common\example\data' \
        if is_windows_os() else r'/home/mg/github/IBATS_Common/ibats_common/example/data'
    df = load_data('RB.csv',
              folder_path=DATA_FOLDER_PATH,
              index_col='trade_date', range_from='2013-1-1', range_to='2015-12-31'
              )
    assert min(df.index) > str_2_date('2013-1-1')
    assert max(df.index) < str_2_date('2015-12-31')


if __name__ == "__main__":
    _test_load_data()
