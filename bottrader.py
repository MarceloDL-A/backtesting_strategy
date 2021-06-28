import pandas as pd
import numpy as np
from flask import Flask, Response
from os import environ
from sqlalchemy import create_engine
from sqlalchemy.types import Numeric, DateTime
import json
import talib

app = Flask(__name__)

# Data Wrangling Imports
from datetime import datetime
from binance.client import Client
# Importing Binance Websockets API
from binance.client import *
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

API_KEY = 'diTPYPCoegNvdTVCmM6CzbdfDcYUy4qBGFtcPU7CiIZNaDpbqJFO1FbPgExzHLJO'
API_SECRET = 'alMrM98m8l02chaSDpRlDqvfblsAbmUt8Pl2Nh2ohN3YVnwqcx2SWncvXKoEupX0'
STARTING_DATE = "15 May, 2020"
END_DATE = "15 Jun, 2021"
	
def process_message(msg):
	if msg['e'] == 'error':
		bm.stop_socket(conn_key)
		bm.close()
	else:
		pass

def initialize_socket_manager():
	client = Client(API_KEY, API_SECRET)
	bm = BinanceSocketManager(client, user_timeout=60)
	return client, bm

def initialize_candles_save_to_df(trading_pair, interval):
	if interval == '30m':
		interval_pair = Client.KLINE_INTERVAL_30MINUTE
	if interval == '1h':
		interval_pair = Client.KLINE_INTERVAL_1HOUR
	elif interval == '2h':
		interval_pair = Client.KLINE_INTERVAL_2HOUR
	elif interval == '4h':
		interval_pair = Client.KLINE_INTERVAL_4HOUR
	elif interval == '6h':
		interval_pair = Client.KLINE_INTERVAL_6HOUR
	elif interval == '8h':
		interval_pair = Client.KLINE_INTERVAL_8HOUR
	elif interval == '12h':
		interval_pair = Client.KLINE_INTERVAL_12HOUR
	else:
		interval_pair = Client.KLINE_INTERVAL_1HOUR
	client = Client(API_KEY, API_SECRET)
	bm = BinanceSocketManager(client, user_timeout=60)
	list_messages = []
	conn_key = bm.start_trade_socket(trading_pair, process_message)
	bm.start()
	candles = client.get_klines(symbol=trading_pair, interval=Client.KLINE_INTERVAL_1HOUR)
	indexes = ['Open Time', 'Open', 'High','Low', 'Close', 'Volume', 'Close Time', 'QAV', 'No. Trades', 'Taker BBAV', 'Taker BQAV', 'Ignore'] 
	data = pd.DataFrame(columns=indexes, data=candles)
	return data

def data_wrangle_df(data):
	data['Open Time'] = data['Open Time'].apply(lambda x: datetime.fromtimestamp(int(x)/1000))
	data = data.filter(['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
	data = adjust_floating_point(data)
	return data
	
def adjust_floating_point(data):
	for item in data.columns:
		if item == "Open Time":
			pass
		else:
			data[item] = data[item].astype(float)
	return data

def save_data_on_database(data, trading_pair):

	engine = create_engine('postgresql://postgres:lifeistotallyfineifyoucare@localhost:5432/projetointegrador')
	data.to_sql(
		trading_pair.lower(),
		engine,
		if_exists='replace',
		index=False,
		chunksize=500,
		schema='cryptos',
		dtype={
			"Open Time": DateTime,
			"Open": Numeric,
			"High": Numeric,
			"Low": Numeric,
			"Close": Numeric,
			"Volume": Numeric
		}
	)

@app.route('/<string:trading_pair>')
def print_dataframe(trading_pair):
	if trading_pair == None:
		trading_pair = 'ADABNB'
	data = initialize_candles_save_to_df(trading_pair, '30m')
	data = data_wrangle_df(data)
	parsed = json.loads(data.to_json(orient='records'))
	dumps = json.dumps(parsed, indent=4, sort_keys=True)
	save_data_on_database(data, trading_pair)
	return Response(dumps, mimetype='application/json')
"""	
@app.route('/buy')
def buy_order():
    client, bm = initialize_socket_manager()
    #data = initialize_candles_save_to_df('ONEBNB', '15m')
    #data = data_wrangle_df(data)
    #upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    order = client.order_limit_buy(
    symbol='VTHOBNB',
    quantity=100,
    price='0.00002280')
    #parsed = json.loads(data.to_json(orient='records'))
    #dumps = json.dumps(parsed, indent=4, sort_keys=True)
    #return Response(dumps, mimetype='application/json')
    return Response('yes')

"""
