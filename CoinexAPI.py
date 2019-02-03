##############################################################
# Author: Jeremy Felder										 #
# Date: July 27 2018										 #
# Version: 0.1.0											 #
# Python Version: 3.6
#															 #
# This software is currently not under license and is solely #
# meant for non-commercial use. Please feel free to use      #  							
# this code in your own programs for personal use. The 	     #
# Author is not liable for any outcomes of using this code.  #
##############################################################

import hashlib
import time
import json as complex_json
import requests
import sys
from requests import exceptions


class CoinexAPI:
	def __init__(self, access, secret):
		self.access_id = access
		self.secret_key = secret

	# **********************  Helper methods for signature ********************** #

	def set_headers(self):
		headers = {
			"Content-Type": "application/json;charset=utf-8",
			"Accept":"application/json",
		 	"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
		 	}
		return headers

	@staticmethod
	def get_sign(params, secret):
		sorted_params = sorted(params)
		data = []
		for key in sorted_params:
			data.append(key + '=' + str(params[key]))
		str_params = "{0}&secret_key={1}".format('&'.join(data), secret)
		signature = hashlib.md5(str_params.encode('utf-8')).hexdigest().upper()
		return signature


	def set_auth(self, params, headers):
		params['access_id'] = self.access_id
		params['tonce'] = int(time.time() * 1000 + 10000)
		headers['authorization'] = self.get_sign(params, self.secret_key)



	def coinex_request(self, method, url, params={}):
		headers = self.set_headers()
		code = -1
		retries = 0

		while(code != 0 and retries <= 20):
			try:
				self.set_auth(params, headers)
				if method == "GET":
					response = requests.get(url, params=params, headers=headers, timeout=5)
				elif method == "DELETE":
					time.sleep(0.1)
					response = requests.delete(url, params=params, headers=headers, timeout=5)
				else:
					time.sleep(0.1)
					response = requests.post(url, json=params, headers=headers, timeout=5)
				#Convert response into json format
				responsejson = response.json()

				#check for critical errors
				code = responsejson['code']
				retries += 1

				if code != 0:
					if code == 1:
						print("General Error. Continuing")
						code = 0
						time.sleep(0.5)
					elif code == 2:
						print("One of your parameters is not correct")
						sys.exit(2)
					elif code == 3:
						print("There was an error on Coinex's server.")
						sys.exit(2)
					elif code == 23:
						ip_address = responsejson['message'].split(" ")[0][3:]
						print("Please add {0} as a whitelisted IP address".format(ip_address))
						sys.exit(2)
					elif code == 25:
						print("Signature Error. Please check your access_id and secret_key are correct")
						sys.exit(2)
					elif code == 35:
						print("API is currently down.")
						sys.exit(2)
					elif code == 36:
						print("Timeout")
						sys.exit(2)
					elif code == 107:
						print("Your account does not have sufficient funds to make this transaction. Trying again.")
					elif code == 227:
						print("Tonce is not within one (1) minute of current time")
						sys.exit(2)
					elif code == 600:
						print("Order number: {0} does not exist. Please double check you entered the order id correctly\n{1}".format(params['id'], url))
						if url.split("/")[-1] == "pending":
							responsejson = "pending"
							code = 0 
					elif code == 601:
						print("The order you are trying to access is not your order")
						sys.exit(2)
					elif code == 602:
						print("{0} amount you are trying to {1} is below the minimum amount for this pair".format(params['amount'], params['type']))
						sys.exit(2)
					elif code == 651:
						print("Merge Depth Error")
						sys.exit(2)
			except exceptions.RequestException:
				continue

		return responsejson

	#### CREATE COUNTING FOR SELL AMOUNT AND BUY AMOUNT IN PREVIOUS 24HR

	# ********************** Account API ******************** #
	def account_info(self):
		url = "https://api.coinex.com/v1/balance/info"
		account_balances = self.coinex_request("GET", url)['data']
		non_zero_balances = {}
		for key in account_balances.keys():
			if account_balances[key]['available'] != '0':
				non_zero_balances[key] = account_balances[key]['available']
		return non_zero_balances


	# ********************** Trading API ******************** #
	def limit_order(self, market, buy_or_sell, amount, price):
		url = "https://api.coinex.com/v1/order/limit"
		params = {'market': market, 
					'type': buy_or_sell,
					'amount': str(amount), 
					'price': str(price),
					'source_id': str(123)
					}
		return self.coinex_request("POST", url, params)['data']

	def market_order(self, market, buy_or_sell, amount):
		url = "https://api.coinex.com/v1/order/market"
		params = {'market': market, 
					'type': buy_or_sell,
					'amount': str(amount)
					}
		
		return self.coinex_request("POST", url, params)['data']

	def ioc_order(self, market, buy_or_sell, amount, price):
		url = "https://api.coinex.com/v1/order/ioc"
		params = {'market': market, 
					'type': buy_or_sell,
					'amount': str(amount), 
					'price': str(price),
					'source_id': str(123)
					}
		return self.coinex_request("POST", url, params)['data']

	def cancel_order(self, id, market):
		url = "https://api.coinex.com/v1/order/pending"
		params = {'id': id,
					'market': market
					}
		response = self.coinex_request("DELETE", url, params)
		if response != "pending":
			response = response['data']
		return response

	def get_mining_difficulty(self):
		url = 'https://api.coinex.com/v1/order/mining/difficulty'
		return self.coinex_request("GET", url)['data']

	def order_status(self, id, market):
		params = {'id':id,
					'market': market
					}
		url = 'https://api.coinex.com/v1/order/status'
		response = self.coinex_request("GET", url, params)
		response = response['data'] if response['code'] == 0 else "status"
		return response

	def unex_list(self, page, market, limit):
		params = {'page':page,
					'market': market,
					'limit': limit
					}
		url = 'https://api.coinex.com/v1/order/pending'
		return self.coinex_request("GET", url, params)['data']['data']

	def executed_list(self, page, market, limit):
		params = {'page':page,
					'market': market,
					'limit': limit
					}
		url = 'https://api.coinex.com/v1/order/finished'
		return self.coinex_request("GET", url, params)['data']['data']

	def user_deals(self, page, market, limit):
			params = {'page':page,
						'market': market,
						'limit': limit
						}
			url = 'https://api.coinex.com/v1/order/user/deals'
			return self.coinex_request("GET", url, params)['data']['data']		

	# ********************** Market API  ******************** #
	@staticmethod
	def list_of_pairs():
		response = None
		while(response is None):
			try:
				response = requests.get('https://api.coinex.com/v1/market/list').json()['data']
			except exceptions.RequestException:
				continue
		return response

	@staticmethod
	def market_ticker(market=""):
		response = None
		while(response is None):
			try: 
				if market:
					url = 'https://api.coinex.com/v1/market/ticker?market={0}'.format(market)
					response = requests.get(url).json()['data']
				else:
					response = requests.get('https://api.coinex.com/v1/market/ticker/all').json()['data']
			except exceptions.RequestException:
				continue
		return response

	@staticmethod
	def depth(market, merge, limit=20):
		params = {'market': market,
					'merge': merge,
					'limit': limit
					}
		response = None
		while(response is None):
			try:
				response = requests.get('https://api.coinex.com/v1/market/depth', params=params).json()['data']
			except exceptions.RequestException:
				continue
		return response

	@staticmethod
	def latest_tx_data(market):
		params = {'market': market}
		response = None
		while(response is None):
			try:
				response = requests.get('https://api.coinex.com/v1/market/deals', params=params).json()['data']
			except exceptions.RequestException:
				continue
		return response

	@staticmethod
	def k_line(market, limit, type):
		params = {'market': market,
					'limit': limit,
					'type':type
					}
		response = None
		while(response is None):
			try:
				response = requests.get('https://api.coinex.com/v1/market/kline', params=params).json()['data']
			except exceptions.RequestException:
				continue
		return response

	@staticmethod
	def least_amount(market):
		response = None
		while(response is None):
			try:
				response = requests.get('https://www.coinex.com/res/market').json()['data']['market_info'][market]
			except exceptions.RequestException:
				continue
		return response
