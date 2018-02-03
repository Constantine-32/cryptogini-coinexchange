import config

def unicode_to_float(string):
	try:
		if '.' in string:
			aux = string.split('.')
			decimals = len(aux[1])
			return float(aux[0]) + float(aux[1])/pow(10,len(aux[1]))
		else:
			return float(string)
	except Exception as e:
		print e, string
		return 0

class Price_Recorder:

	def __init__(self, num_of_records = 10):
		self.num_of_records = num_of_records
		self.prices_ready = False
		self.init_counter = 0
		self.coins = {}

	def initialize_coins(self, tickers, coins_to_track, pair2 = config.market):

		for ticker in tickers:
			if ticker['MarketID'] in coins_to_track:
				coin = {}
				coin['symbol'] = coins_to_track[ticker['MarketID']]
				coin['price'] = unicode_to_float(str(ticker['LastPrice']))
				coin['previous_prices'] = [coin['price']] * self.num_of_records
				coin['mean'] = coin['price']
				# coin['minQty'] = 0.0
				# coin['tickSize'] = 0.0
				coin['previous_spikes'] = {}
				self.coins[ticker['MarketID']] = coin

	#--MISC--#	
	def get_mean(self, coin):
		mean = 0
		previous_prices = coin['previous_prices']
		for price in previous_prices[:-4]:
			mean += price
			coin['mean'] = mean / (len(previous_prices)-4)

	#--CORE--#
	def update_previous_prices(self):
		if self.prices_ready == True:
			for key, coin in self.coins.items():
				coin['previous_prices'].pop(0) #Get rid of the first and append the new at the end
				coin['previous_prices'].append(coin['price'])
				self.get_mean(coin)
				self.coins[str(key)] = coin #Update coin
		else:
			for key, coin in self.coins.items():
				coin['previous_prices'][self.init_counter] = coin['price']
				self.coins[str(key)] = coin #Update coin

			self.init_counter += 1
			# print self.init_counter * self.logtime, "s"
			if self.init_counter >= self.num_of_records:
				print ("Array of Records initialized!")
				self.prices_ready = True



		