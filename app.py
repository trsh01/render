import io
import mplfinance as mpf
import pandas as pd
import yfinance as yf
from flask import Flask, send_file, request
import talib
import matplotlib
matplotlib.use('Agg') # Necessary for non-GUI backend

app = Flask(__name__)
#app = Freezer(__name__)

@app.route('/',methods=['GET'])
def index():
    return '<meta http-equiv="refresh" content="5"><img src="/chartdata" alt="Financial Chart" />'

@app.route('/chartdata')
def chart_data():
    # 1. Load data
    #df = pd.read_csv('data.csv', index_col=0, parse_dates=True)
    df = yf.Ticker('BTC-USD').history(period='4mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
    # 2. Create memory buffer
    #with open("coin.txt", "r") as archivo:
    #    coin=archivo.read()
    RSI_PERIOD=14
    closes_array = df['Close'].to_numpy()
    df['rsi']=talib.RSI(closes_array,RSI_PERIOD) 
    #df.ta.macd(close='close', fast=6, slow=12, signal=5, append=True)   
    memory_file = io.BytesIO()
   
    # 3. Plot to buffer
    #mpf.plot(df, type='candle', savefig=dict(fname=memory_file, format="png"))
    rsi_plot = mpf.make_addplot(df['rsi'], panel=2, color='blue', ylabel='RSI')
    mpf.plot(df, type='candle', style='starsandstripes', volume=True, title=coin+' CHART', mav=(20, 50), addplot=rsi_plot, panel_ratios=(4, 2, 2), savefig=dict(fname=memory_file, format="png"))
        
    # 4. Seek to start
    memory_file.seek(0)
    
    # 5. Return as image
    return send_file(memory_file, mimetype='image/png')

#if __name__ == '__main__':
   #app.run(host='0.0.0.0', port=5000) # '0.0.0.0' expone la app
#   app.freeze()
