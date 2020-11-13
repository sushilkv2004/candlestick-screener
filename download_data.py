__author__ = 'skv'

import os
import yfinance as yf

with open('datasets/symbols.csv') as f:
    lines = f.read().splitlines()
    for symbol in lines:
        print(symbol)
        try:
            data = yf.download(symbol, start="2020-01-01", end="2020-09-04")
            data.to_csv("datasets/daily/{}.csv".format(symbol))
        except Exception as e:
            print(f'{symbol} download failed \{e}')
            continue