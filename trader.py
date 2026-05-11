import time
import logging
import requests, json 
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
from config import Config
import mplfinance as mpf

# Setup logging
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class high:
    def __init__(self, coin, percent, minQty):                
        self.coin = coin  
        self.percent = (float(percent)) 
        self.minQty =minQty

class BinanceTradingBot:
    def __init__(self):
        Config.validate()
        self.client = Client(Config.API_KEY, Config.API_SECRET, testnet=Config.TEST_MODE)
        self.symbol = ""#Config.SYMBOL
        self.trade_amount = ""#Config.TRADE_AMOUNT
        self.position = None  # 'long' or 'short' or None

        # Strategy parameters
        self.fast_period = 5
        self.slow_period = 20

        logging.info(f"Bot initialized for {self.symbol} in {'TEST' if Config.TEST_MODE else 'LIVE'} mode")
    
    def getExchange(self):
        exchange_info = self.client.get_exchange_info()
        symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING']
        print(f'Total trading pairs: {len(symbols)}')
        req="https://www.binance.com/fapi/v1/ticker/24hr"
        h=high("", 0.0, 0.0)
        response = requests.get(req)
        json_r=json.loads(response.text)
        for coin in json_r:
            if coin['symbol'] in symbols:
                if float(coin['priceChangePercent'])>h.percent:
                    info = self.client.get_symbol_info(coin['symbol'])
                    for f in info['filters']:
                        if f['filterType'] == 'NOTIONAL':
                            min_qty = f['minNotional']            
                    h =  high(coin['symbol'], coin['priceChangePercent'], min_qty)
        print(f"Coin: {h.coin} - Price Change Percent: {h.percent} - Min Qty: {h.minQty}")
        return h
    
    def get_historical_data(self, symbol, interval='1m', limit=100):
        """Get historical klines data"""
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close'] = df['close'].astype(float)
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df
        except BinanceAPIException as e:
            logging.error(f"Error getting historical data: {e}")
            return None

    def calculate_moving_averages(self, df):
        """Calculate fast and slow moving averages"""
        df['fast_ma'] = df['close'].rolling(window=self.fast_period).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_period).mean()
        return df

    def generate_signal(self, df):
        """Generate trading signal based on MA crossover"""
        if len(df) < self.slow_period:
            return 'hold'

        fast_ma = df['fast_ma'].iloc[-1]
        slow_ma = df['slow_ma'].iloc[-1]
        prev_fast_ma = df['fast_ma'].iloc[-2]
        prev_slow_ma = df['slow_ma'].iloc[-2]

        # Bullish crossover
        if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
            return 'buy'

        # Bearish crossover
        elif prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
            return 'sell'

        return 'hold'
    
    def calculateMA(self, df):
        
         if df is not None:
            # Calculate moving averages
            df = self.calculate_moving_averages(df)

            # Generate trading signal
            signal = self.generate_signal(df)   
            # Log current price and position
            current_price = df['close'].iloc[-1]
            logging.info(f"Price: {current_price}, Position: {self.position}, Signal: {signal}")
            return signal

    def calculateRSI(self,df):
        RSI_PERIOD=14
        RSI_OVERBOUGHT=80
        RSI_OVERSOLD=20
        closes_array = df['close'].to_numpy()
        df['rsi']=talib.RSI(closes_array,RSI_PERIOD)
        print("RSI: "+str(df['rsi'].iloc[-1]))
        if df['rsi'].iloc[-1]>RSI_OVERBOUGHT:
            signal='sell'
        if df['rsi'].iloc[-1]<RSI_OVERSOLD:
            signal='buy'
        else:
            signal='hold'
        return df,signal
    
    def execute_trade(self, signal):
        """Execute buy or sell order"""
        try:
            if signal == 'buy' and self.position != 'long':
                if Config.TEST_MODE:
                    logging.info(f"TEST BUY: {self.symbol} - Amount: {self.trade_amount}")
                    print(f"TEST BUY: {self.symbol} - Amount: {self.trade_amount}")
                else:
                    #order = self.client.order_market_buy(
                    #    symbol=self.symbol,
                    #    #quantity=self.trade_amount
                    #    quoteOrderQty=self.trade_amount
                    #)
                    order=self.client.create_order(
                        symbol=self.symbol,
                        side="BUY",
                        type="MARKET",
                        #quantity="85",
                        quoteOrderQty=self.trade_amount
                    )
                    logging.info(f"BUY ORDER EXECUTED: {order}")
                    print(f"BUY ORDER EXECUTED: {order}")

                self.position = 'long'

            elif signal == 'sell' and self.position != 'short':
                if Config.TEST_MODE:
                    logging.info(f"TEST SELL: {self.symbol} - Amount: {self.trade_amount}")
                    print(f"TEST SELL: {self.symbol} - Amount: {self.trade_amount}")
                else:
                    #order = self.client.order_market_sell(
                    #    symbol=self.symbol,
                    #    quoteOrderQty=self.trade_amount
                    #)
                    order=self.client.create_order(
                        symbol=self.symbol,
                        side="SELL",
                        type="MARKET",
                        #quantity="85",
                        quoteOrderQty=self.trade_amount
                    )
                    logging.info(f"SELL ORDER EXECUTED: {order}")
                    print(f"SELL ORDER EXECUTED: {order}")

                self.position = 'short'

        except BinanceAPIException as e:
            logging.error(f"Error executing trade: {e}")
            print(f"Error executing trade: {e}")

    def execute_RSItrade(self,signal):
        if signal == 'buy':
            order = self.client.order_market_buy(
                        symbol=self.symbol,
                        quantity=self.trade_amount
                    )
            logging.info(f"BUY ORDER EXECUTED: {order}")
            print(f"BUY ORDER EXECUTED: {order}")
        if signal == 'sell':
            order = self.client.order_market_sell(
                        symbol=self.symbol,
                        quantity=self.trade_amount
                    )
            logging.info(f"SELL ORDER EXECUTED: {order}")
            print(f"SELL ORDER EXECUTED: {order}")

    def graficar(self,df):
        df = df.set_index('timestamp')
        #df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
        #print(df.index)
        rsi_plot = mpf.make_addplot(df['rsi'], panel=2, color='blue', ylabel='RSI')
        mpf.plot(df, type='candle', style='charles', volume=True, title=self.symbol, mav=(20, 50), addplot=rsi_plot, panel_ratios=(4, 2, 2))
        
    
    def run(self):
            """Main trading loop"""
            print(f"Starting Binance Trading Bot for {self.symbol}")
            print(f"Mode: {'TEST' if Config.TEST_MODE else 'LIVE'}")
            print("Press Ctrl+C to stop")
            #Get cripto if maximun 24hs percent change 
            highcoin=self.getExchange()
            print(highcoin.coin)
            self.symbol=highcoin.coin  
            self.trade_amount=highcoin.minQty[:4]
            with open("coin.txt", "w") as archivo:
                archivo.write(highcoin.coin)
            
            while True:
                try:
                                      
                    # Get historical data
                    df = self.get_historical_data(self.symbol)
                    #print(df)
                    MAsignal=self.calculateMA(df)
                    df,RSIsignal=self.calculateRSI(df)
                    # Execute trade if signal is generated
                    df.to_csv('data.csv', index=False)
                    if MAsignal != 'hold':
                        print("MASIGNAL:"+MAsignal)
                        self.execute_trade(MAsignal)
                        #self.graficar(df)
                    if RSIsignal != 'hold':
                        print("RSISIGNAL:",RSIsignal)
                        self.execute_RSItrade(RSIsignal)
                        #self.graficar(df)
                    current_price = df['close'].iloc[-1]
                    logging.info(f"Price: {current_price}, Position: {self.position}, SignalRSI: {RSIsignal},SignalMA: {MAsignal}")
                    print(f"Price: {current_price}, Position: {self.position}, SignalRSI: {RSIsignal},SignalMA: {MAsignal}")
                    # Wait before next iteration
                    time.sleep(5)  # Check every minute

                except KeyboardInterrupt:
                    print("\nBot stopped by user")
                    logging.info("Bot stopped by user")
                    break
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    print(f"Unexpected error: {e}")
                    time.sleep(60)


if __name__ == "__main__":
    bot = BinanceTradingBot()
    bot.run()
