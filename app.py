import io, json, requests
import mplfinance as mpf
import pandas as pd
import yfinance as yf
from flask import Flask, send_file, request, render_template
import talib
import matplotlib
matplotlib.use('Agg') # Necessary for non-GUI backend

app = Flask(__name__)
#app = Freezer(__name__)
def generate_signal(df):
        """Generate trading signal based on MA crossover"""
        maColor="goldenrod"
        if len(df) < 20:
            return 'hold', maColor

        fast_ma = df['fast_ma'].iloc[-1]
        slow_ma = df['slow_ma'].iloc[-1]
        prev_fast_ma = df['fast_ma'].iloc[-2]
        prev_slow_ma = df['slow_ma'].iloc[-2]
        

        # Bullish crossover
        if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
            maColor="green"
            return 'Comprar', maColor
        # Bearish crossover
        elif prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
            maColor="red"
            return 'Vender', maColor

        return 'Mantenerse', maColor

@app.route('/',methods=['GET'])
def index():
    #return '<meta http-equiv="refresh" content="5"><img src="/cripto/BTC-USD" alt="Financial Chart" />'
    return render_template('index.html')
@app.route('/menu',methods=['GET'])
def menu():
    tickers=[]
    topGainers=[]
    mostGainers=[]
    req="https://www.binance.com/fapi/v1/ticker/24hr"
    #req="https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=10&formatted=true&scrIds=ALL_CRYPTOCURRENCIES_US&sortField=&sortType=&start=0&useRecordsResponse=true&fields=ticker%2ClogoUrl%2Csymbol%2ClongName%2Csparkline%2CshortName%2CregularMarketPrice%2CregularMarketChange%2CregularMarketChangePercent%2CmarketCap%2CregularMarketVolume%2Cvolume24Hr%2CvolumeAllCurrencies%2CcirculatingSupply%2CfiftyTwoWeekChangePercent%2CfiftyTwoWeekRange&lang=en-US&region=US"
    response = requests.get(req)
    
    json_r=json.loads(response.text)
    for coin in json_r:
        print(coin)
        print(coin['lastPrice'])
        if "_" in coin : None
        elif "-" in coin: None
        elif "BTCDOM" in coin:None
        elif "XAUUSD" in coin:None
        elif "XPT" in coin:None
        elif "LITE" in coin:None
        elif "TAUSD" in coin:None
        elif "SPORTFUN" in coin:None
        else:
            if 'USDT' in coin:
                ticker=[coin['symbol'], float(coin['lastPrice']), float(coin['priceChangePercent']), float(coin['priceChange'])]
                tickers.append(ticker)

    tickers.sort(key=lambda item: item[1])
    MVC=tickers[-15:]
    MVC=MVC[::-1]
    tickers.sort(key=lambda item: item[2])
    MG=tickers[-15:]
    MG=MG[::-1]
    tickers.sort(key=lambda item: item[3])
    TG=tickers[-15:]
    TG=TG[::-1]
    for item in MVC:
        
        if "-" in item[0]:
            symbolIndex=item[0].find("USD")
            item[0]=item[0][:symbolIndex-1]+'-'+item[0][-3:]
        else:
            symbolIndex=item[0].find("USD")
            item[0]=item[0][:symbolIndex]+'-'+item[0][-4:-1]
        
    for item in MG:
        
        if "-" in item[0]:
            symbolIndex=item[0].find("USD")
            item[0]=item[0][:symbolIndex-1]+'-'+item[0][-3:]
        else:
            symbolIndex=item[0].find("USD")
            item[0]=item[0][:symbolIndex]+'-'+item[0][-4:-1]
        
    for item in TG:
        
        if "-" in item[0]:
            symbolIndex=item[0].find("USD")
            item[0]=item[0][:symbolIndex-1]+'-'+item[0][-3:]
        else:
            symbolIndex=item[0].find("USD")
            item[0]=item[0][:symbolIndex]+'-'+item[0][-4:-1]
        
    #for item in TG:
    #    symbolIndex=item[0].find("USDT")
    #    item[0]=item[0][:symbolIndex]+'-'+item[0][-4:-1]
    
    return render_template('menu.html', mvc=MVC,tg=TG,mg=MG) 

@app.route('/grafico/<string:symbol>/', defaults={'months':'4mo'})
@app.route('/grafico/<string:symbol>/<string:months>',)
def grafico(symbol, months):

    return render_template('grafico.html',symbol=symbol,months=months)
@app.route('/cripto/<string:symbol>/', defaults={'months':'4mo'})
@app.route('/cripto/<string:symbol>/<string:months>',)
def chart_data(symbol, months):
    #1. Load data
    #df = pd.read_csv('data.csv', index_col=0, parse_dates=True)
    if symbol=="SPY-USD":
        symbol="SPY"
    elif symbol=="QQQ-USD":
       symbol="QQQ"
    elif symbol=="MSFT-USD":
        symbol="MSFT"
    elif symbol=="PHAROS-USD":
        symbol="PROS39682-USD"
    elif symbol=="AMD-USD":
       symbol="AMD" 
    elif symbol=="MU-USD":
       symbol="MU"
    elif symbol=="GOOGL-USD":
        symbol="GOOGL"
    elif symbol=="TSLA-USD":
        symbol="TSLA"
    elif symbol=="AAPL-USD":
        symbol="AAPL"
   
    df = yf.Ticker(symbol).history(period=months)[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # 2. Create memory buffer
    #with open("coin.txt", "r") as archivo:
    #    coin=archivo.read()
    RSI_PERIOD=14
    closes_array = df['Close'].to_numpy()
    df['rsi']=talib.RSI(closes_array,RSI_PERIOD) 
    df['overbought'] = 70
    df['oversold'] = 20
    #df.ta.macd(close='close', fast=6, slow=12, signal=5, append=True)   
    memory_file = io.BytesIO()
    # 3. Plot to buffer
    #mpf.plot(df, type='candle', savefig=dict(fname=memory_file, format="png"))
    if not df.index.empty:
        apds=[
            mpf.make_addplot(df['rsi'], panel=2, color='blue', ylabel='RSI', ylim=(0, 100)),
            mpf.make_addplot(df['oversold'],panel=2,color='g',ylim=(0, 100)),
            mpf.make_addplot(df['overbought'],panel=2,color='r',ylim=(0, 100))
            #mpf.make_addplot([70], panel=2, color='red', linestyle='dotted'),
            #mpf.make_addplot([30], panel=2, color='green', linestyle='dotted')
        ]
        mpf.plot(df, type='candle', style='starsandstripes', volume=True, title=symbol+' CHART', mav=(20, 50), addplot=apds, panel_ratios=(4, 2, 2), savefig=dict(fname=memory_file, format="png"))
    else:
        return send_file('notfound.png', mimetype='image/png')
            
    # 4. Seek to start
    memory_file.seek(0)
    
    # 5. Return as image
    return send_file(memory_file, mimetype='image/png')
@app.route('/indices/<string:symbol>',methods=['GET'])
def indices(symbol):
    if symbol=="SPY-USD":
        symbol="SPY"
    elif symbol=="QQQ-USD":
       symbol="QQQ"
    elif symbol=="MSFT-USD":
        symbol="MSFT"
    elif symbol=="PHAROS-USD":
        symbol="PROS39682-USD"
    elif symbol=="AMD-USD":
       symbol="AMD" 
    elif symbol=="MU-USD":
       symbol="MU"
    elif symbol=="GOOGL-USD":
        symbol="GOOGL"
    elif symbol=="TSLA-USD":
        symbol="TSLA"
    elif symbol=="AAPL-USD":
        symbol="AAPL"
    
    df = yf.Ticker(symbol).history(period='4mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    closes_array = df['Close'].to_numpy()
    df['rsi']=talib.RSI(closes_array,14)
    df['fast_ma'] = df['Close'].rolling(window=5).mean()
    df['slow_ma'] = df['Close'].rolling(window=20).mean()
    signal, maColor = generate_signal(df)       
    rsiSignal="Mantenerse"
    rsiColor="goldenrod"    
    rsi=df['rsi'].iloc[-1]
    rsi = round(rsi, 2)
    if rsi > 80:
        rsiSignal="Vender"
        rsiColor="red"  
    if rsi < 20:
        rsiSignal="Comprar"
        rsiColor="green"  
    return render_template('indices.html',signal=signal,rsi=rsi,rsiSignal=rsiSignal,rsiColor=rsiColor, maColor=maColor, symbol=symbol)
#if __name__ == '__main__':
   #app.run(host='0.0.0.0', port=5000) # '0.0.0.0' expone la app
#   app.freeze()
