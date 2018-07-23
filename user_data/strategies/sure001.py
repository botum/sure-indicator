# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

import talib.abstract as ta
from pandas import DataFrame

from freqtrade.strategy.interface import IStrategy
from user_data.indicators.sure import *

class sure001(IStrategy):

    """

    author@: Bruno Sarlo

    Strategy for buying and selling on horizontal support and resistances

    """

    # Minimal ROI designed for the strategy
    minimal_roi = {
        # "120":  0.00001,
        # "80":  0.01,
        # "60":  0.001,
        "30":  0.005,
        "0":  0.01
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.01

    # Optimal ticker interval for the strategy
    ticker_interval = "1m"

    def populate_indicators(self, dataframe: DataFrame, pair) -> DataFrame:

        """
        Indicator for support and resistances
        """

        dataframe, su, re = get_sure_OHLC(self, dataframe,
                    intervals=[self.ticker_interval], quantile=0.03,
                    up_thresh=0.005, down_thresh=0.005)

        # print (dataframe)
        # print (dataframe.sup_trend)
        # plot_trends_new(dataframe, interval=self.ticker_interval)
        # plot_pivots()
        # plot_pivots(dataframe, su, re, pair=pair, interval=self.ticker_interval)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """

        dataframe.loc[
            (
                (in_range(dataframe['close'],dataframe.s1*1.00001, 0.00001))
                &
                (dataframe['r1'] > dataframe['s1']*1.01)
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['close'] >= dataframe['r1']*0.999999)
                # |
                # (dataframe['close'] <= dataframe['s1'] * 0.95)

            ),
            'sell'] = 1
        # print (dataframe.loc[dataframe['sell']==1].close)

        return dataframe



    def did_bought(self):
        """
        we are notified that a given pair was bought
        :param pair: the pair that was is concerned by the dataframe
        """

    def did_sold(self):
        """
        we are notified that a given pair was sold
        :param pair: the pair that was is concerned by the dataframe
        """

    def did_cancel_buy(self):
        """
        we are notified that a given pair buy was not filled
        :param pair: the pair that was is concerned by the dataframe
        """

    def did_cancel_sell(self):
        """
        we are notified that a given pair was not sold
        :param pair: the pair that was is concerned by the dataframe
        """
