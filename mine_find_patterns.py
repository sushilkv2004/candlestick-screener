__author__ = 'skv'


import talib
import yfinance as yf
from patterns import candlestick_patterns

import matplotlib.pyplot as plt
import pandas
import plotly.graph_objects as go
from plotly.subplots import make_subplots

bu_pt = ["CDLHAMMER", #looks good
         "CDLINVERTEDHAMMER", #looks good
         "CDLPIERCING",
         "CDLENGULFING",
         "CDLHARAMI",  #detection not good
         "CDLMORNINGDOJISTAR"]

be_pt = ['CDLDOJISTAR', 'CDLHANGINGMAN', 'CDLSHOOTINGSTAR', 'CDLDARKCLOUDCOVER', 'CDLENGULFING', 'CDLEVENINGSTAR',
         'CDLLONGLEGGEDDOJI', 'CDLTAKURI', "CDLHARAMI" ]

selec_pt = [
    'CDLHAMMER',
    'CDLINVERTEDHAMMER',
    'CDLDRAGONFLYDOJI',
    'CDLENGULFING',
    'CDLDARKCLOUDCOVER',
    'CDLMORNINGDOJISTAR',
    'CDLDOJI',
    'CDLDOJISTAR',
    'CDLEVENINGDOJISTAR',
    'CDLEVENINGSTAR',
    'CDLHANGINGMAN',
    'CDLHARAMI',
    'CDLLONGLEGGEDDOJI',
    'CDLPIERCING',
    'CDLSHOOTINGSTAR',
    'CDLTAKURI'
    ]


def chart_with_volume(symbol, df, cs_patters, skip_bulls = False, skip_bears=True):

    candlestick = go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])

    #######################################################
    #ADD VOLUME

    #SET VOLUME COLORS
    INCREASING_COLOR = 'Green'
    DECREASING_COLOR = 'Red'

    colors = []

    for i in range(len(df.Close)):
        if i != 0:
            if df.Volume[i] > df.Volume[i - 1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)

    volume = go.Bar( x=df['Date'],  y=df['Volume'] , marker_color=colors, name='Volume')

    #######################################################
    # Adding annotations for the high and low of the day.
    annotations = []

    count  = 0
    arrow_color = {}
    for p in cs_patters:
        #if not p in selec_pt: continue
        #print(f"p={p}")

        x_vals_bull = df["Date"][df[p] > 0]
        y_vals_bull = df["High"][df[p] > 0]
        x_vals_bear = df["Date"][df[p] < 0]
        y_vals_bear = df["High"][df[p] < 0]

        if not skip_bulls:
            for x_val, y_val in zip(x_vals_bull, y_vals_bull):
                count +=1
                annotations.append(go.layout.Annotation(x=x_val,
                                                    y=y_val,
                                                    showarrow=True,
                                                    arrowhead=2,
                                                    arrowcolor='green',
                                                    arrowsize=3,
                                                    arrowwidth=2,
                                                    text=f"{p[3:]}"))

        if not skip_bears:
            for x_val, y_val in zip(x_vals_bear, y_vals_bear):
                count +=1
                annotations.append(go.layout.Annotation(x=x_val,
                                                    y=y_val,
                                                    showarrow=True,
                                                    arrowhead=3,
                                                    arrowcolor='red',
                                                    arrowsize=2,
                                                    arrowwidth=1,
                                                    text=f"{p[3:]}"))

    layout = dict(
        title=f'{symbol}',
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        annotations=annotations,
        xaxis=dict(zerolinecolor='black', showticklabels=False),
        xaxis2=dict(showticklabels=True),
    )

    fig = make_subplots(vertical_spacing=0, rows=2, cols=1, row_heights=[1, .5 ], shared_xaxes=True)

    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(volume, row=2, col=1)

    fig.update_layout(layout)

    fig.layout.xaxis.type = 'category' #disables weekends
    fig.layout.xaxis2.type = 'category'  # disables weekends


    fig.show()
    #print(f'annotations = {count}')

def plot_portfolio_one_cs():
    portfolio = ["AMZN", "COF", "BA", "AAPL", "GOOG"]
    dataframes = {}
    for symbol in portfolio:
        #df = yf.download(symbol, start="2020-01-01", end="2020-08-01")
        df = pandas.read_csv('datasets/daily/{}'.format(f'{symbol}.csv'))
        for pattern in selec_pt: #candlestick_patterns:
             #for pattern in bu_pt:
             pattern_function = getattr(talib, pattern)
             df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
             print(f"-----------{pattern} days:-------")
             p_days = df[df[pattern] != 0]
             print(df.loc[df[pattern] != 0].Date)
             print(p_days[pattern])
        dataframes[symbol] = df

    for pattern in selec_pt:
        print(f'showing {pattern}')
        for symbol in portfolio:
            print(f'   -> of {symbol}')
            chart_with_volume(symbol, dataframes[symbol], [pattern])
        input('Type OK to go to next CS')

def plot_all_on_single_stock():
    dataframes = {}
    symbol = "SPY"
    df = pandas.read_csv('datasets/3Yrs/{}'.format(f'{symbol}1.csv'))
    p_list = []
    for pattern in bu_pt: #candlestick_patterns:
        pattern_function = getattr(talib, pattern)
        df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
        print(f"-----------{pattern} days:-------")
        #print(pattern, " : ", df[df[pattern] != 0][pattern])
        p_days = df[df[pattern] != 0]
        print(df.loc[df[pattern] != 0].Date)
        print(p_days[pattern])
        p_list.append(pattern)

    chart_with_volume(symbol, df, p_list)


def finding_working_bulls_on_single_stock():
    symbol = "AMZN"
    df = pandas.read_csv('datasets/2018_2020Aug/{}'.format(f'{symbol}.csv'))
    p_list = []
    count =0
    for pattern in candlestick_patterns: #bu_pt
        pattern_function = getattr(talib, pattern)
        df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
        p_days = df[df[pattern] > 0]

        if len(p_days) >0:
            print(f"\n{pattern[3:]}, {symbol}({len(p_days)})\n")
            chart_with_volume(symbol, df, [pattern])
            count += 1
            if count%10==0:
                input("--More--")



def plot_all_bulls_on_single_stock():
    bull_patterns = ["CDLENGULFING", "CDLBREAKAWAY",  "CDL3OUTSIDE",
                   "CDL3INSIDE", "CDLSTICKSANDWICH", "CDLPIERCING",
                    "CDLMORNINGSTAR","CDLGAPSIDESIDEWHITE", "CDLUNIQUE3RIVER"]
    symbol = "TWTR"
    df = pandas.read_csv('datasets/daily/{}'.format(f'{symbol}.csv'))
    p_list = []
    patterns_found = []
    count = 0
    for pattern in bull_patterns: #bu_pt
        pattern_function = getattr(talib, pattern)
        df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
        p_days = df[df[pattern] > 0]
        if len(p_days) >0:
            patterns_found.append(pattern)
            print(f"\n{pattern[3:]}, {symbol}({len(p_days)})\n")
    chart_with_volume(symbol, df, patterns_found)


def finding_working_bears_on_single_stock():
    working_paterns = ["EVENINGDOJISTAR", "ENGULFING", "CLOSINGMARUBOZU",
                       "HARAMICROSS", "EVENINGSTAR", "SPINNINGTOP"]


    symbols = ['MSFT', 'TSLA', 'UBER', 'V', 'WMT']
    for symbol in symbols:
        df = pandas.read_csv('datasets/2018_2020Aug/{}'.format(f'{symbol}.csv'))
        count =0
        for pattern in candlestick_patterns:
            if pattern[3:] not in working_paterns: continue

            pattern_function = getattr(talib, pattern)
            df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            p_days = df[df[pattern] < 0]

            if len(p_days) > 0:
                print(f"\n{pattern[3:]} {symbol}({len(p_days)})\n")
                chart_with_volume(symbol, df, [pattern], skip_bulls=True, skip_bears=False)
                count += 1
                if count%10==0:
                    input("--More--")

def VPA_Candles():
    """
    Chapter 6:
    • ﻿a rising market with falling volume is also a classic sign of weakness.

    3 Main Candles:
    1. Shooting Star - upper wick long, narrow body. weekness - increasing volume - 3 candles
    2. Hammer - reverse of shooting star - a low volume candle is indicating minor weakness,
        average volume suggests stronger signs of a possible reversal, whilst ultra high signals
        the insiders buying heavily, as part of the buying climax.

        Hanging man - same as hammer but at the top of bullish trend

    3. Long Legged Doji - can signal a reversal from bearish to bullish, or bullish to bearish, and the change in
        direction depends on the preceding price action.
        should always be validated by a minimum of average volume, and preferably high or ultra high.
        If it is low, then it is an anomaly and therefore a trap set by the insiders.
        If the volume is high, we must be patient and wait for the subsequent price action to unfold.
        We may see further doji candles before the trend is established, so as always patience is required following
        their appearance. Wait for direction to be confirmed and established.

	4. ﻿Wide Spread Candles  ﻿Price action – strong market sentiment
    ﻿5. Narrow Spread Candles Price action – weak market sentiment
﻿    6. The Hanging Man Candle Price action – potential weakness after bullish trend
        The hanging man is validated if it is followed by the appearance of a shooting star in the next few candles,
        particularly if associated with above average or high volume. The key here is validation.
        On its own it is not a strong signal, but merely gives us early warning of a possible change.

    ﻿6. Stopping Volume  ﻿Price action - strength
        - falling and price spreads are narrows and volume is rising  - bearish to bullish reversal
	7. ﻿Topping Out Volume Price action - weakness
        reverse of previous one - rising but narrowing, volume rising - bullish to bearish

    """
    vpa_patterns = ["CDLHAMMER", "CDLSHOOTINGSTAR" , "CDLHANGINGMAN", "CDLLONGLEGGEDDOJI"]
    vpa_patterns1 = ["CDLSHOOTINGSTAR"]


    #symbols = ['AMZN', 'COF', 'MSFT', 'TSLA', 'UBER', 'V', 'WMT']
    symbols = ['SPY']

    for symbol in symbols:
        #df = pandas.read_csv('datasets/2018_2020Aug/{}'.format(f'{symbol}.csv'))
        df = pandas.read_csv('datasets/3Yrs/{}'.format(f'{symbol}.csv'))
        pattern_found = []
        for pattern in candlestick_patterns:
            if pattern not in vpa_patterns1: continue

            pattern_function = getattr(talib, pattern)
            df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            p_days = df[df[pattern] != 0]

            if len(p_days) > 0:
                pattern_found.append(pattern)
                print(f"\n{pattern[3:]} {symbol}({len(p_days)})\n")
        if len(pattern_found)>0:
            chart_with_volume(symbol, df, pattern_found, skip_bulls=False, skip_bears=False)


if __name__ == "__main__":
    #finding_working_bears_on_single_stock()
    VPA_Candles()