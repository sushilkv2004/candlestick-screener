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
         'CDLLONGLEGGEDDOJI', 'CDLTAKURI' ]

selec_pt = ["CDLGRAVESTONEDOJI"]
pt = [
    'CDLDOJISTAR',
    'CDLDRAGONFLYDOJI',
    'CDLENGULFING',
    'CDLDARKCLOUDCOVER',
    'CDLDOJI',
    'CDLDOJISTAR',
    'CDLENGULFING',
    'CDLEVENINGDOJISTAR',
    'CDLEVENINGSTAR',
    'CDLHANGINGMAN',
    'CDLHARAMI',
    'CDLLONGLEGGEDDOJI',
    'CDLPIERCING'
    ]


def chart_with_volume(symbol, df, cs_patters):

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
    for p in cs_patters:
        #if not p in selec_pt: continue
        print(f"p={p}")

        x_vals = df["Date"][df[p] != 0]
        y_vals = df["High"][df[p] != 0]
        print(x_vals, y_vals)
        for x_val, y_val in zip(x_vals, y_vals):
            count +=1
            annotations.append(go.layout.Annotation(x=x_val,
                                                y=y_val,
                                                showarrow=True,
                                                arrowhead=1,
                                                arrowcolor="purple",
                                                arrowsize=2,
                                                arrowwidth=2,
                                                text=f"{p[3:]}"))

    layout = dict(
        title=f'{symbol}',
        xaxis_rangeslider_visible=False,
        annotations=annotations,
        xaxis=dict(zerolinecolor='black', showticklabels=False),
        xaxis2=dict(showticklabels=True),
    )
    '''
    yaxis2=dict(
                 scaleanchor="y",
                 scaleratio=.5,
                 #domain=[0,.2]
         ),
    yaxis=dict(
        scaleanchor="y",
        scaleratio=.5,
        #domain=[.2,1]
    ),
    '''

    fig = make_subplots(vertical_spacing=0, rows=2, cols=1, row_heights=[1, .5 ], shared_xaxes=True)

    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(volume, row=2, col=1)

    fig.update_layout(layout)

    fig.layout.xaxis.type = 'category' #disables weekends
    fig.layout.xaxis2.type = 'category'  # disables weekends


    fig.show()
    print(f'annotations = {count}')

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

