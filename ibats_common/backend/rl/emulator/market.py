#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2019/6/28 17:09
@File    : market.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import pandas as pd
import numpy as np


class QuotesMarket(object):
    def __init__(self, md_df: pd.DataFrame, data_factors, state_with_flag=False, init_cash=2e5):
        self.data_close = md_df['close']
        self.data_open = md_df['open']
        self.data_observation = data_factors
        self.action_space = ['close', 'long', 'short', 'keep']
        self.fee = 3e-3  # 千三手续费
        self.max_step_count = self.data_observation.shape[0] - 1
        self.init_cash = init_cash
        # reset use
        self.step_counter = 0
        self.cash = self.init_cash
        self.position = 0
        self.total_value = self.cash + self.position
        self.flags = 0
        self.state_with_flag = state_with_flag

    def reset(self):
        self.step_counter = 0
        self.cash = self.init_cash
        self.position = 0
        self.total_value = self.cash + self.position
        self.flags = 0
        if self.state_with_flag:
            return self.data_observation[0], np.array([self.flags])
        else:
            return self.data_observation[0]

    def latest_state(self):
        if self.state_with_flag:
            return self.data_observation[-1], np.array([self.flags])
        else:
            return self.data_observation[-1]

    def get_action_space(self):
        return self.action_space

    def long(self):
        self.flags = 1
        quotes = self.data_open[self.step_counter] * 10
        self.cash -= quotes * (1 + self.fee)
        self.position = quotes

    def short(self):
        self.flags = -1
        quotes = self.data_open[self.step_counter] * 10
        self.cash += quotes * (1 - self.fee)
        self.position = - quotes

    def keep(self):
        quotes = self.data_open[self.step_counter] * 10
        self.position = quotes * self.flags

    def close_long(self):
        self.flags = 0
        quotes = self.data_open[self.step_counter] * 10
        self.cash += quotes * (1 - self.fee)
        self.position = 0

    def close_short(self):
        self.flags = 0
        quotes = self.data_open[self.step_counter] * 10
        self.cash -= quotes * (1 + self.fee)
        self.position = 0

    def step_op(self, action):

        if action == 'long':
            if self.flags == 0:
                self.long()
            elif self.flags == -1:
                self.close_short()
                self.long()
            else:
                self.keep()

        elif action == 'close':
            if self.flags == 1:
                self.close_long()
            elif self.flags == -1:
                self.close_short()
            else:
                pass

        elif action == 'short':
            if self.flags == 0:
                self.short()
            elif self.flags == 1:
                self.close_long()
                self.short()
            else:
                self.keep()
        elif action == 'keep':
            self.keep()
        else:
            raise ValueError("action should be elements of ['long', 'short', 'close']")

        price = self.data_close[self.step_counter]
        position = price * 10 * self.flags
        reward = self.cash + position - self.total_value
        self.step_counter += 1
        self.total_value = position + self.cash
        next_observation = self.data_observation[self.step_counter]

        done = False
        if self.total_value < price:
            done = True
        if self.step_counter >= self.max_step_count:
            done = True

        if self.state_with_flag:
            return (next_observation, np.array([self.flags])), reward, done
        else:
            return next_observation, reward, done

    def step(self, action):
        if 0 <= action <= 3:
            return self.step_op(self.action_space[action])
        else:
            raise ValueError("action should be one of [0,1,2]")


def _test_quote_market():
    n_step = 60
    ohlcav_col_name_list = ["open", "high", "low", "close", "amount", "volume"]
    from ibats_common.example.data import load_data
    md_df = load_data('RB.csv').set_index('trade_date')[ohlcav_col_name_list]
    md_df.index = pd.DatetimeIndex(md_df.index)
    from ibats_common.backend.factor import get_factor, transfer_2_batch
    factors_df = get_factor(md_df, dropna=True)
    df_index, df_columns, data_arr_batch = transfer_2_batch(factors_df, n_step=n_step)
    md_df = md_df.loc[df_index, :]
    # 建立 QuotesMarket
    qm = QuotesMarket(md_df=md_df[['close', 'open']], data_factors=data_arr_batch, state_with_flag=True)
    next_observation = qm.reset()
    assert len(next_observation) == 2
    assert next_observation[0].shape[0] == n_step
    assert next_observation[1] == 0
    next_observation, reward, done = qm.step(1)
    assert len(next_observation) == 2
    assert next_observation[1] == 1
    assert not done
    next_observation, reward, done = qm.step(0)
    assert next_observation[1] == 0
    assert reward != 0
    next_observation, reward, done = qm.step(0)
    assert next_observation[1] == 0
    assert reward == 0
    next_observation, reward, done = qm.step(3)
    assert next_observation[1] == 0
    assert reward == 0
    next_observation, reward, done = qm.step(2)
    assert next_observation[1] == -1
    assert not done
    next_observation, reward, done = qm.step(3)
    assert next_observation[1] == -1
    assert reward != 0
    try:
        qm.step(4)
    except ValueError:
        print('is ok for not supporting action>3')


if __name__ == "__main__":
    _test_quote_market()
