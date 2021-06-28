import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import talib
import requests
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from bokeh.plotting import output_notebook


st.title('Bot Trader')
st.markdown('**ADABNB**\n')

trading_pair = st.selectbox(
'Choose a pair',
('ADABNB', 'ANKRBNB', 'ATOMBNB', 'BAKEBNB', 'CAKEBNB', 'CHZBNB', 'EOSBNB', 'HOTBNB', 
'MATICBNB', 'MITHBNB', 'ONEBNB', 'TRXBNB', 'XRPBNB', 'ADABTC', 'AKROBTC', 'ALPHABTC', 
'BNBBTC', 'CAKEBTC', 'CHZBTC', 'COSBTC', 'DASHTBTC', 'DOGEBTC', 'ETHBTC',
'GASBTC', 'GOBTC', 'HIVEBTC', 'IOTABTC'))

st.markdown('**' + trading_pair + '**\n')

binance_request = requests.get('http://127.0.0.1:5000/' + trading_pair)
binance_json = binance_request.json()
data = pd.DataFrame(binance_json)
data['Open Time'] = data['Open Time'].apply(lambda x: datetime.fromtimestamp(int(x)/1000))


st.write(data.head())
st.write('Backtesting Estratégia SMA')

def SMA(values, n):
	"""
	Return simple moving average of `values` at
	each step taking into account `n` previous values.
	"""
	return pd.Series(values).rolling(n).mean()
	
class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        
    def next(self):
        # If sma1 crosses above sma2, close any existing short
        # trades and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        
        # Else, if sma1 crosses below sma2, close any
        # existing long trades and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
            
bt = Backtest(data, SmaCross, cash=10_000, commission=.0001)
stats_sma = bt.run()
st.write("Retorno para SMA: {:.2f} %".format(stats_sma[6]))
st.write("Drawdown Máximo para SMA: {:.2f} %".format(stats_sma[13]))
st.write("Taxa de acertos: {:.2f} %".format(stats_sma[18]))

st.write('Backtesting Estratégia RSI')

def RSI(values, n):
    rsi = talib.RSI(values, timeperiod=n)
    return rsi

class RSICross(Strategy):
    n24 = 24
    n6 = 6
    
    def init(self):
         # Precompute the RSI
        self.rsi24 = self.I(RSI, self.data.Close, self.n24)
        self.rsi6 = self.I(RSI, self.data.Close, self.n6)
        
    def next(self):
        if self.rsi6 < 20 and crossover(self.rsi6, self.rsi24):
            self.position.close()
            self.buy()
        
        elif crossover(self.rsi24, self.rsi6):
            self.position.close()
            self.sell()

bt = Backtest(data, RSICross, cash=10_000, commission=.0001)
stats_rsi = bt.run()
st.write("Retorno para RSI: {:.2f} %".format(stats_rsi[6]))
st.write("Drawdown Máximo para RSI: {:.2f} %".format(stats_rsi[13]))
st.write("Taxa de acertos: {:.2f} %".format(stats_rsi[18]))

def MACD(values, fastp, slowp, sigp):
	macd, macdsignal, macdhist = talib.MACD(values, fastperiod=12, slowperiod=26, signalperiod=9)
	return macd, macdsignal, macdhist
	
class MACDCross(Strategy):
	fastp = 12
	slowp = 26
	sigp = 9
	
	def init(self):
		# Precompute MACD values
		self.macd, self.macdsignal, self.macdhist = self.I(MACD, self.data.Close, self.fastp, self.slowp, self.sigp)
	
	def next(self):
		if crossover(self.macd, self.macdsignal):
			self.position.close()
			self.buy()
		
		elif crossover(self.macdsignal, self.macd):
			self.position.close()
			self.sell()
	
bt = Backtest(data, MACDCross, cash=10_000, commission=.0001)
stats_macd = bt.run()
st.write("Retorno para MACD: {:.2f} %".format(stats_macd[6]))
st.write("Drawdown Máximo para MACD: {:.2f} %".format(stats_macd[13]))
st.write("Taxa de acertos: {:.2f} %".format(stats_macd[18]))


