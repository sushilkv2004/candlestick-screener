__author__ = 'skv'

import pandas as pd
import talib
from pandas_datareader import data as pdr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def plot_it(symbol, df, fractals = False, show=True, rsi=False):

    candlestick = go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])

    #######################################################
    #ADD VOLUME

    #SET VOLUME COLORS
    INCREASING_COLOR = 'Green'
    DECREASING_COLOR = 'Red'

    colors = []

    for i in range(len(df.Close)):
        if i != 0:
            if df.Close[i] > df.Close[i - 1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)


    #######################################################

    if 'ADX' in df.columns:
        fig = make_subplots(vertical_spacing=0, rows=4, cols=1, row_heights=[1, .3 , .3, .3], shared_xaxes=True, )
    else:
        fig = make_subplots(vertical_spacing=0, rows=3, cols=1, row_heights=[1, .3 , .3], shared_xaxes=True)


    fig.add_trace(candlestick, row=1, col=1)

    ema13 = go.Scatter( x=df['Date'],  y=df['EMA_13'],line=dict(color='green', width=2), mode='lines', name='ema13')
    fig.add_trace(ema13, row=1, col=1)

    ema26 = go.Scatter( x=df['Date'],  y=df['EMA_26'],line=dict(color='red', width=2), mode='lines', name='ema26')
    fig.add_trace(ema26, row=1, col=1)

    if not rsi:
        avg_volume = go.Scatter( x=df['Date'],  y=df['AVG_VOLUME'],line=dict(color='royalblue', width=1), mode='lines', name='AvgVolume')
        volume = go.Bar( x=df['Date'],  y=df['Volume'] , marker_color=colors, name='Volume')
    else:
        rsi = go.Scatter( x=df['Date'],  y=df['RSI'],line=dict(color='royalblue', width=1), mode='lines', name='rsi')

    if 'ADX' in df.columns:
        if not rsi:
            fig.add_trace(volume, row=4, col=1)
            fig.add_trace(avg_volume, row=4, col=1)
        else:
            fig.add_trace(rsi, row=4, col=1)
    else:
        if not rsi:
            fig.add_trace(volume, row=3, col=1)
            fig.add_trace(avg_volume, row=3, col=1)
        else:
            fig.add_trace(rsi, row=4, col=1)


    MACD_HIST = go.Bar(x=df['Date'], y=df['MACD_HIST'], name='MACD_HIST')
    fig.add_trace(MACD_HIST, row=2, col=1)

    MACD = go.Scatter(x=df['Date'], y=df['MACD'], line=dict(color='green', width=2), mode='lines', name='MACD')
    fig.add_trace(MACD, row=2, col=1)

    MACD_SIG = go.Scatter(x=df['Date'], y=df['MACD_SIG'], line=dict(color='red', width=2), mode='lines',
                          name='MACD_SIG')
    fig.add_trace(MACD_SIG, row=2, col=1)

    if 'SAR' in df.columns:
        sar_colors = []
        for i in range(len(df.Close)):
            if df.Close[i] > df.SAR[i]:
                sar_colors.append(INCREASING_COLOR)
            else:
                sar_colors.append(DECREASING_COLOR)


        SAR = go.Scatter(x=df['Date'], y=df['SAR'], marker_color=sar_colors, mode='markers', name='sar')
        fig.add_trace(SAR, row=1, col=1)


    if 'ADX' in df.columns:
        adx = go.Scatter(x=df['Date'], y=df['ADX'], line=dict(color='black', width=2), mode='lines', name='adx')
        pdi = go.Scatter(x=df['Date'], y=df['PLUS_DI'], line=dict(color='green', width=2), mode='lines', name='+di')
        mdi = go.Scatter(x=df['Date'], y=df['MINUS_DI'], line=dict(color='red', width=2), mode='lines', name='-di')

        fig.add_trace(adx, row=3, col=1)
        fig.add_trace(pdi, row=3, col=1)
        fig.add_trace(mdi, row=3, col=1)

    annotations = []

    if 'Buy' in df.columns:
        x_vals_buy = df["Date"][df["Buy"] == True]
        y_vals_buy = df["High"][df["Buy"] == True]
        x_vals_sell = df["Date"][df["Sell"] == True]
        y_vals_sell = df["High"][df["Sell"] == True]

        for x_val, y_val in zip(x_vals_buy, y_vals_buy):
            annotations.append(go.layout.Annotation(x=x_val,
                                                    y=y_val,
                                                    showarrow=True,
                                                    arrowhead=2,
                                                    arrowcolor='green',
                                                    arrowsize=2,
                                                    arrowwidth=2,
                                                    ax=0,
                                                    ay=-60,
                                                    text="Buy"
                                                    ))
        for x_val, y_val in zip(x_vals_sell, y_vals_sell):
            annotations.append(go.layout.Annotation(x=x_val,
                                                    y=y_val,
                                                    showarrow=True,
                                                    arrowhead=2,
                                                    arrowcolor='red',
                                                    arrowsize=2,
                                                    arrowwidth=2,
                                                    ax=0,
                                                    ay=-60,
                                                    text="Sell"
                                                    ))

    if  fractals:
        x_vals_support = df["Date"][df["Support"] == True]
        y_vals_support = df["Low"][df["Support"] == True]

        x_vals_resistance = df["Date"][df["Resistance"] == True]
        y_vals_resistance  = df["High"][df["Resistance"] == True]

        end_dt = df["Date"][len(df["Date"])-1]
        for x_val, y_val in zip(x_vals_support, y_vals_support):
            annotations.append(go.layout.Annotation(x=x_val,
                                                    y=y_val,
                                                    showarrow=True,
                                                    arrowhead=4,
                                                    arrowcolor='green',
                                                    arrowsize=2,
                                                    arrowwidth=2,
                                                    ax=0,
                                                    ay=60,
                                                    text="F-S"
                                                    ))
        for x_val, y_val in zip(x_vals_resistance, y_vals_resistance):
            annotations.append(go.layout.Annotation(x=x_val,
                                                    y=y_val,
                                                    showarrow=True,
                                                    arrowhead=4,
                                                    arrowcolor='red',
                                                    arrowsize=2,
                                                    arrowwidth=2,
                                                    ax=0,
                                                    ay=-60,
                                                    text="F-R"
                                                    ))

    layout = dict(
        #width=650,
        title=f'{symbol}',
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        xaxis3_rangeslider_visible=False,
        annotations=annotations,
        xaxis=dict(zerolinecolor='black', showticklabels=False),
        xaxis2=dict(showticklabels=False),
        #xaxis3_tickformat='%B %Y',
        xaxis3=dict(showticklabels=True,tickformat='%y/%m'),
        yaxis=dict(
            showline=True,
            overlaying='y',
            side='right'
        ),
        yaxis2=dict(
            showline=True,
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            showline=True,
            overlaying='y',
            side='right'
        )

    )

    if 'ADX' in df.columns:
        layout['xaxis4_rangeslider_visible'] = False
        layout['yaxis4'] = dict(
                showline=True,
                overlaying='y',
                side='right')
        layout['xaxis3']['showticklabels'] = False
        layout['xaxis4'] = dict(showticklabels=True,tickformat='%y/%m')


    fig.update_layout(layout)

    fig.layout.xaxis.type = 'category'  #disables weekends
    fig.layout.xaxis2.type = 'category'  # disables weekends
    fig.layout.xaxis3.type = 'category'  # disables weekends

    if 'ADX' in df.columns:
        fig.layout.xaxis4.type = 'category'  # disables weekends

    config = dict({'scrollZoom': True})

    if show:
        fig.show(config=config)
    else:
        return fig
    #print(f'annotations = {count}')


def get_data(symbol, start_dt, end_dt, multi_year=False, minute=False, show=True):
    df = pdr.get_data_yahoo(symbol, start_dt, end_dt)
    if show: print(df.head(5))

    df['Date'] = pd.to_datetime(df.index)
    df = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    df = df.reset_index(drop=True)
    if show: print('*'*50)
    if show: print(df.head(5))
    if show: print('*'*50)

    if multi_year:
        df["Date"] = df["Date"].dt.strftime("%y-%m-%d")
    elif minute: #need to check
        df["Date"] = df["Date"].dt.strftime("%d-%HH:%mm")
    else: #day
        df["Date"] = df["Date"].dt.strftime("%m-%d")
    if show: print(df.head(5))
    if show: print('*'*50)
    return df

def  common_indictors(df, rsi=False):
    df['AVG_VOLUME'] = df['Volume'].rolling(window=13).mean()

    # df['SMA_13'] = df['Close'].rolling(window=13).mean()
    # df['SMA_26'] = df['Close'].rolling(window=26).mean()
    df['EMA_13'] = talib.EMA(df['Close'], 13)
    df['EMA_26'] = talib.EMA(df['Close'], 26)
    macd, macdsignal, macdhist = talib.MACD(df['Close'])  # default: fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD'] = macd
    df['MACD_HIST'] = macdhist
    df['MACD_SIG'] = macdsignal
    if rsi:
        df['RSI'] = talib.RSI(df['Close'])
    return df


def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] \
            and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
  return support

def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] \
               and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
  return resistance


def isFarFromLevel(l, level):
   global s
   return np.sum([abs(l-x) < s  for x in level]) == 0


def sr_fractal_indicator(df):
    """
    The retracement levels can be used in a situation where you wanted to buy a particular stock but you have not been
    able to because of a sharp run-up in the stock price. In such a situation, wait for the price to correct to Fibonacci
     retracement levels such as 23.6%, 38.2%, and 61.8% and then buy the stock.The ratios 38.2% and 61.8% are the most
     important support levels.
    :param df:
    :return:
    """
    global s

    levels = []
    levelr = []


    df['Support'] = False
    df['Resistance'] = False
    s = np.mean(df['High'] - df['Low'])

    c1 = df.columns.get_loc('Support')
    c2 = df.columns.get_loc('Resistance')

    for i in range(2, df.shape[0] - 2):
        if isSupport(df, i):
           l = df['Low'][i]
           if isFarFromLevel(l, levels):
               levels.append((i, l))
               df.iloc[i, c1] = True

        elif isResistance(df, i):
            l = df['High'][i]
            if isFarFromLevel(l, levelr):
                levelr.append((i, l))
                df.iloc[i, c2] = True

    return df

