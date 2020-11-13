import talib
import yfinance as yf

data = yf.download("SPY", start="2020-01-01", end="2020-08-01")

"""
morning_star = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])

engulfing = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])

data['Morning Star'] = morning_star
data['Engulfing'] = engulfing

engulfing_days = data[data['Engulfing'] != 0]

print(engulfing_days)
"""

print('CDLINVERTEDHAMMER')
inverted_hammer = talib.CDLINVERTEDHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
data['inverted_hammer'] = inverted_hammer
inverted_hammer_days = data[data['inverted_hammer'] != 0]
print(inverted_hammer_days)

print('CDLHAMMER')
hammer = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
data['hammer'] = hammer
hammer_days = data[data['hammer'] != 0]
print(hammer_days)