import requests
import time

import config
from Price_Recorder import *
from pump import *
from record_prices import *

ses = requests.session()
# print ses.get('https://www.coinexchange.io/api/v1/getmarketsummaries').json()

def get_markets():
	return ses.get('https://www.coinexchange.io/api/v1/getmarkets').json()['result']

def get_market_summaries():
	return ses.get('https://www.coinexchange.io/api/v1/getmarketsummaries').json()['result']

def track_all_coins(tickers, coins_to_track):
	for ticker in tickers:
		if ticker['BaseCurrencyCode'] == 'BTC' and ticker['Active']:
			# coins_to_track.append(ticker['MarketAssetCode'])
			coins_to_track[str(ticker['MarketID'])] = str(ticker['MarketAssetCode']) 

def exclude_coins(coins_to_track, coins_to_exclude):
	# coins_to_exclude = []
	for excluded_coin in coins_to_exclude:
		for key, tracked_coin in coins_to_track.items():
			if excluded_coin == tracked_coin:
				del coins_to_track[key]

def update_prices(tickers, coins):
	for ticker in tickers:
		if ticker['MarketID'] in coins:
			coins[str(ticker['MarketID'])]['price'] = unicode_to_float(str(ticker['LastPrice']))

def init_retained_prices(coins_to_track):
	retained_prices = {} 
	for coin in coins_to_track.values():
		retained_prices[coin] = []
	return retained_prices

def check_spikes(coins, pump_info, pump_running):
	
	for coin in coins.values():
		
		spike = (coin['price'] - coin['mean'])/coin['mean']

		if pump_running == True and pump_info.coin_bought == False:
			if spike >= config.pump_percentage and spike < config.pump_change_abort:
				pump_info.calculate_order_parameters(coin['symbol'], coin['price'], coin['mean'])
				if config.make_order:
					print("Place order")						

		for spike_alarm in config.spikes_alarms:

			if str(spike_alarm) not in coin['previous_spikes'].keys():
				if spike_alarm < 0:
					if spike < spike_alarm:
						print (coin['symbol'], " Has fallen a", ("{:.3f}%!").format(spike*-100))
						coin['previous_spikes'][str(spike_alarm)] = datetime.now()
				if spike_alarm > 0:
					if spike > spike_alarm:
						print (coin['symbol'], " Has increased a", ("{:.3f}%!").format(spike*100))
						coin['previous_spikes'][str(spike_alarm)] = datetime.now()

if __name__ == "__main__":

	#COINS TO TRACK
	coins_to_track = {}
	coins_to_exclude = config.coins_to_exclude

	track_all_coins(get_markets(), coins_to_track)
	exclude_coins(coins_to_track, coins_to_exclude)

	#PUMP INFO
	pump_info = Pump_Info(config.btc_available)

	#COINS INFO
	price_recorder = Price_Recorder(10)
	price_recorder.initialize_coins(get_market_summaries(), coins_to_track)

	#Time variables
	t_fetch = time.time()
	t_dips = time.time()
	t_reset_alarms = time.time()
	t_pump_start = time.time()

	#--LIST OF RETAINED PRICES DURING PUMP--#
	retained_prices = init_retained_prices(coins_to_track)

	#--RESET SPIKE ALARM--#
	t_betw_res_alarm_delta =timedelta(seconds = config.t_betw_res_alarm)

	#--PUMP INFO--#
	pump_running = False

	while True:
		if time.time() - t_fetch > config.t_betw_fetch:
			t_fetch = time.time()

			update_prices(get_market_summaries(), price_recorder.coins)

			#---RECORD COINS---#
			if config.record_coins_txt:
				if pump_running == True: 
					for symb, coin in price_recorder.coins.items():
						retain_coin_price(coin['price'], retained_prices[coin['symbol']], coin['symbol'])
				else: 
					for coin in price_recorder.coins.values():
						record_coin_price(coin['price'], coin['symbol'])

			#---START PUMP MODE---#
			if config.next_pump['ended'] == False and pump_running == False:
				if is_pump_near(config.next_pump, 0, config.pump_time_margin): # 5 seconds before
					pump_running = True
					config.t_betw_fetch = 0.1
					t_pump_start = time.time()
					print ("...Starting Pump Prodecure...")
			print time.time()
			#---CHECK FOR FAST % CHANGES---#
			check_spikes(price_recorder.coins, pump_info, pump_running)

		#---UPDATE RECORDS---#
		if time.time() - t_dips > config.t_betw_rec:
			t_dips = time.time()
			price_recorder.update_previous_prices()

		#---PUMP MODE ENDED---#
		if time.time() - t_pump_start > config.t_pump_duration and pump_running:
			pump_running = False
			config.next_pump['ended'] = True
			config.t_betw_fetch = 0.5

			pump_info.reset_parameters()

			print ("Dumping data, Pump finalized!")

			if config.record_coins_txt:
				for key, coin_retained_prices in retained_prices.items():
					dump_retained_prices(coin_retained_prices, key)

		#---RESET SPIKE ALARMS---# 
		if time.time() - t_reset_alarms > config.t_betw_res_alarm and pump_running == False:
			t_reset_alarms = time.time()
			for symb, coin in price_recorder.coins.items():
				for spike_alarm in config.spikes_alarms:
					if str(spike_alarm) in coin['previous_spikes'].keys():
						if datetime.now() - coin['previous_spikes'][str(spike_alarm)] > t_betw_res_alarm_delta:
							coin['previous_spikes'].pop(str(spike_alarm), None)
#Get markets:
	#market id, market asset code, active or not --> get name

#Get market summaires:
	# LastPrice --> needs id
#Get order book
