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
    #avg_volume = go.Scatter( x=df['Date'],  y=df['AVG_VOLUME'],line=dict(color='royalblue', width=1), mode='lines', name='AvgVolume')

    ema13 = go.Scatter( x=df['Date'],  y=df['EMA_13'],line=dict(color='red', width=2), mode='lines', name='ema13')
    ema26 = go.Scatter( x=df['Date'],  y=df['EMA_26'],line=dict(color='green', width=2), mode='lines', name='ema26')

    MACD = go.Scatter( x=df['Date'],  y=df['MACD'], line=dict(color='red', width=2), mode='lines', name='MACD')
    MACD_HIST = go.Bar( x=df['Date'],  y=df['MACD_HIST'],name='MACD_HIST')

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
                                                    arrowhead=3,
                                                    arrowcolor='green',
                                                    arrowsize=2,
                                                    arrowwidth=1,
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
        xaxis3_rangeslider_visible=False,
        annotations=annotations,
        xaxis=dict(zerolinecolor='black', showticklabels=False),
        xaxis2=dict(showticklabels=False),
        xaxis3=dict(showticklabels=True),

    )

    fig = make_subplots(vertical_spacing=0, rows=3, cols=1, row_heights=[1, .3 , .3], shared_xaxes=True)

    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(ema13, row=1, col=1)
    fig.add_trace(ema26, row=1, col=1)
    fig.add_trace(volume, row=3, col=1)
    #fig.add_trace(avg_volume, row=3, col=1)
    fig.add_trace(MACD_HIST, row=2, col=1)
    fig.add_trace(MACD, row=2, col=1)

    fig.update_layout(layout)

    fig.layout.xaxis.type = 'category' #disables weekends
    fig.layout.xaxis2.type = 'category'  # disables weekends
    fig.layout.xaxis3.type = 'category'  # disables weekends

    fig.show()
    #print(f'annotations = {count}')

def find_portfolio_one_cs():
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

def find_all_on_single_stock():
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


def find_working_bulls_on_single_stock():
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



def find_all_bulls_on_single_stock():
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
    bear_paterns = ["EVENINGDOJISTAR", "ENGULFING", "CLOSINGMARUBOZU",
                       "HARAMICROSS", "EVENINGSTAR", "SPINNINGTOP"]


    symbols = ['MSFT', 'TSLA', 'UBER', 'V', 'WMT']
    for symbol in symbols:
        df = pandas.read_csv('datasets/2018_2020Aug/{}'.format(f'{symbol}.csv'))
        count =0
        for pattern in candlestick_patterns:
            if pattern[3:] not in bear_paterns: continue

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
        ﻿If the first candle was an initial sign of weakness, then the second, with increased volume
        is confirming this weakness further.﻿ If a third appears then this is adding yet more bearish sentiment.

         -only one stock found n had no impact

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
        pattern_function = getattr(talib, pattern)
        df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
        p_days = df[df[pattern] != 0]

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



def detect_multiple_cs_with_rising_volume(df, pattern, req_stint):
    max_stint = 0
    stint = 0
    c = df.columns.get_loc(pattern)

    for i in range(1, len(df.Close)):
        if df[pattern][i] != 0 and \
           df[pattern][i-1] !=0 and \
           df.Volume[i] >= df.Volume[i-1] and \
           df['Volume'][i] > df['AVG_VOLUME'][i]:
           stint += 1
           if stint > max_stint:
               max_stint = stint
               if max_stint>= req_stint: print(df['Date'][i], max_stint)
        else:
            # remove candles
            if i<len(df.Close)-1 and df[pattern][i] != 0 and df[pattern][i+1] == 0 \
                    and (df[pattern][i-1] == 0  or df[pattern][i-2] == 0 ):
                df.iloc[i, c] = 0
                df.iloc[i-1, c] = 0
                df.iloc[i-2, c] = 0
            stint = 0

    return max_stint, df

def analyze_vpa_multiple():
    #"CDLSHOOTINGSTAR" - ONE FOUND - NO IMPACT

    vpa_patterns = ["CDLHAMMER", "CDLSHOOTINGSTAR" , "CDLHANGINGMAN", "CDLLONGLEGGEDDOJI"]
    bull_patterns = ["CDLENGULFING", "CDLBREAKAWAY", "CDL3OUTSIDE",
                     "CDL3INSIDE", "CDLSTICKSANDWICH", "CDLPIERCING",
                     "CDLMORNINGSTAR", "CDLGAPSIDESIDEWHITE", "CDLUNIQUE3RIVER"]
    bear_paterns = ["CDLEVENINGDOJISTAR", "CDLENGULFING", "CDLCLOSINGMARUBOZU",
                    "CDLHARAMICROSS", "CDLEVENINGSTAR", "CDLSPINNINGTOP"]

    all_patterns =  vpa_patterns + bull_patterns + bear_paterns
    one_pattern = ["CDLLONGLEGGEDDOJI"]

    symbols = []
    with open('datasets/symbols.csv') as f:
        for line in f:
            symbol = line.strip()
            symbols.append(symbol)


    from os import path

    cnt = 0
    for symbol in symbols:
        # df = pandas.read_csv('datasets/2018_2020Aug/{}'.format(f'{symbol}.csv'))

        pattern_found = []
        file_path = f'datasets/5Yrs/{symbol}.csv'
        if not path.exists(file_path):
            print(f"data for {symbol} not found")
            continue
        df = pandas.read_csv(file_path)
        if df.empty:
            print(f"data for {symbol} is empty")
            continue

        df['AVG_VOLUME'] = df['Volume'].rolling(window=10).mean()
        #pattern_found = []
        for pattern in  vpa_patterns:
            pattern_function = getattr(talib, pattern)
            df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            p_days = df[df[pattern] != 0]
            if len(p_days) > 0:
                max_stint, df = detect_multiple_cs_with_rising_volume(df, pattern, req_stint=3)
                if max_stint >= 2:
                    print(f"{symbol} - {pattern} found with max sting = {max_stint}")
                    pattern_found.append(pattern)
        if len(pattern_found)>0:
            chart_with_volume(symbol, df, pattern_found, skip_bulls=False, skip_bears=False)
            cnt +=1
            if cnt % 10 == 0:
                input("--More--")

def detect_cs_with_rising_volume(factor, pattern, df):
    c = df.columns.get_loc(pattern)

    result = False
    for i in range(1, len(df.Close)):
        if df[pattern][i] != 0:
            if df['Volume'][i] >= df['AVG_VOLUME'][i]*factor and \
                    df['Volume'][i]>=df['Volume'][i-1]:
                result = True
            else: # remove candles
                df.iloc[i, c] = 0

    return result, df

def find_working_patterns_with_volume():
    bull_patterns = ["CDLENGULFING", "CDLBREAKAWAY", "CDL3OUTSIDE",
                     "CDL3INSIDE", "CDLSTICKSANDWICH", "CDLPIERCING",
                     "CDLMORNINGSTAR", "CDLGAPSIDESIDEWHITE", "CDLUNIQUE3RIVER"]
    bear_paterns = ["CDLEVENINGDOJISTAR", "CDLENGULFING", "CDLCLOSINGMARUBOZU",
                    "CDLHARAMICROSS", "CDLEVENINGSTAR", "CDLSPINNINGTOP"]
    all_patterns = bull_patterns + bear_paterns

    """
    symbols = []
    with open('datasets/symbols.csv') as f:
        for line in f:
            symbol = line.strip()
            symbols.append(symbol)

    """
    symbols = ['NVDA', 'AMZN', 'COF']
        #['AMZN', 'COF',
       #'MSFT', 'TSLA', 'UBER', 'V', 'WMT', 'GOOG', 'AAPL',
       #'AAL', 'ADBE', 'BA', 'MGM', 'NVDA', 'ORCL', 'SBX', 'TWTR', 'FB']

    from os import path
    cnt = 0

    for symbol in symbols:
        file_path = f'datasets/daily/{symbol}.csv'
        if not path.exists(file_path):
            print(f"data for {symbol} not found")
            continue
        df = pandas.read_csv(file_path)
        if df.empty:
            print(f"data for {symbol} is empty")
            continue

        pattern_found = []

        df['AVG_VOLUME'] = df['Volume'].rolling(window=13).mean()

        #df['SMA_13'] = df['Close'].rolling(window=13).mean()
        #df['SMA_26'] = df['Close'].rolling(window=26).mean()
        df['EMA_13'] =  talib.EMA(df['Close'], 13)
        df['EMA_26'] =  talib.EMA(df['Close'], 26)
        macd, macdsignal, macdhist = talib.MACD(df['Close']) #default: fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'] = macd
        df['MACD_HIST'] = macdhist


        #pattern_found = []
        for pattern in  all_patterns:
            pattern_function = getattr(talib, pattern)
            df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            p_days = df[df[pattern] != 0]
            if len(p_days) > 0:
                found, df = detect_cs_with_rising_volume(3,  pattern, df)
                if found:    pattern_found.append(pattern)
        chart_with_volume(symbol, df, pattern_found, skip_bulls=False, skip_bears=False)
        cnt +=1
        if cnt % 10 == 0:
            input("--More--")


def chart_without_indicators(symbol, df, cs_patters, skip_bulls = False, skip_bears=False):

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
                                                    arrowhead=3,
                                                    arrowcolor='green',
                                                    arrowsize=2,
                                                    arrowwidth=1,
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
        xaxis3_rangeslider_visible=False,
        annotations=annotations,
        xaxis=dict(zerolinecolor='black', showticklabels=False),
        xaxis2=dict(showticklabels=True),
        xaxis3=dict(showticklabels=True),

    )

    fig = make_subplots(vertical_spacing=0, rows=2, cols=1, row_heights=[1, .3], shared_xaxes=True)

    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(volume, row=2, col=1)
    fig.update_layout(layout)

    fig.layout.xaxis.type = 'category' #disables weekends
    fig.layout.xaxis2.type = 'category'  # disables weekends

    fig.show()
    #print(f'annotations = {count}')

def finding_cs_pattern():
    from commons import get_data
    from datetime import date, timedelta

    today = date.today().strftime("%m-%d-%Y")
    print(today)
    a_year = (date.today() - timedelta(days=12 * 30)).strftime("%m-%d-%Y")

    cs_patterns = ["CDLHAMMER", "CDLINVERTEDHAMMER"]
    symbols = ['SPY']
    #symbols = ['SPY', 'JPM','COF', 'UBER', 'TSLA',  'AMZN', 'NVDA', 'AAPL', 'WMT','GOOG', 'MSFT'] #, 'AMZN', 'COF', 'MSFT', 'TSLA', 'UBER', 'V', 'WMT', 'GOOG', 'AAPL']

    for symbol in symbols:
        #df = pandas.read_csv('datasets/daily/{}'.format(f'{symbol}.csv'))
        #df = get_data(symbol, a_year, today, show=False)
        df = yf.download("SPY", start="2020-01-01", end="2020-08-01")

        count =0
        for pattern in cs_patterns: #bu_pt: #
            pattern_function = getattr(talib, pattern)
            print(pattern_function)
            df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])

            p_days = df[df[pattern] < 0]

            if len(p_days) > 0:
                print(f"\n{pattern[3:]} {symbol}({len(p_days)})\n")
                chart_without_indicators(symbol, df, [pattern], skip_bulls=False, skip_bears=False)
                count += 1
                if count%10==0:
                    input("--More--")
            else:
                print(f"{pattern[3:]} {symbol} not found")


def finding_cs_pattern2():
    from commons import get_data
    from datetime import date, timedelta

    today = date.today().strftime("%m-%d-%Y")
    print(today)
    a_year = (date.today() - timedelta(days=12 * 30)).strftime("%m-%d-%Y")

    #cs_patterns = ["CDLHAMMER", "CDLINVERTEDHAMMER"]
    cs_patterns = ["CDLHAMMER"]

    symbols = ['ROKU']
    #symbols = ['SPY', 'JPM','COF', 'UBER', 'TSLA',  'AMZN', 'NVDA', 'AAPL', 'WMT','GOOG', 'MSFT'] #, 'AMZN', 'COF', 'MSFT', 'TSLA', 'UBER', 'V', 'WMT', 'GOOG', 'AAPL']

    for symbol in symbols:
        #df = pandas.read_csv('datasets/daily/{}'.format(f'{symbol}.csv'))
        df = get_data(symbol, a_year, today, show=False)
        for pattern in bu_pt: #cs_patterns:
            print(pattern)
            pattern_function = getattr(talib, pattern)
            df[pattern] = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])

            count = 0
            p_days = df[df[pattern] != 0]
            print(p_days)
            if len(p_days) > 0:
                print(f"\n{pattern[3:]} {symbol}({len(p_days)})\n")
                chart_without_indicators(symbol, df, [pattern], skip_bulls=False, skip_bears=False)
                count += 1
                if count % 10 == 0:
                    input("--More--")
            else:
                print(f"{pattern[3:]} {symbol} not found")



if __name__ == "__main__":
    #finding_working_bears_on_single_stock()
    #find_working_patterns_with_volume()
    finding_cs_pattern2()
