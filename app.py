import io
import mplfinance as mpf
import pandas as pd
import yfinance as yf
from flask import Flask, send_file, request
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
    df = yf.Ticker('AAPL').history(period='4mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
    #with open("coin.txt", "r") as archivo:
    #    coin=archivo.read()
    # 2. Create memory buffer
    memory_file = io.BytesIO()
    
    # 3. Plot to buffer
    mpf.plot(df, type='candle', savefig=dict(fname=memory_file, format="png"))
    #rsi_plot = mpf.make_addplot(df['rsi'], panel=2, color='blue', ylabel='RSI')
    #mpf.plot(df, type='candle', style='starsandstripes', volume=True, title='CHART', mav=(20, 50), addplot=rsi_plot, panel_ratios=(4, 2, 2), savefig=dict(fname=memory_file, format="png"))
        
    # 4. Seek to start
    memory_file.seek(0)
    
    # 5. Return as image
    return send_file(memory_file, mimetype='image/png')

#if __name__ == '__main__':
   #app.run(host='0.0.0.0', port=5000) # '0.0.0.0' expone la app
#   app.freeze()
