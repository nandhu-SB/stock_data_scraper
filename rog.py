import logging
import yfinance as yf

logging.basicConfig(level=logging.DEBUG)
ticker = yf.Ticker("ADANIPOWER.NS")
info = ticker.info
print(info['currentPrice'])
