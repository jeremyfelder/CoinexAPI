#!/usr/bin/env python

from CoinexAPI import CoinexAPI
from datetime import datetime
import time
import sys, getopt
import os
import fileops
import tradeops
import tradeutils
import emailops


def start(access_id, secret_key, market, target_percentage, swing_amount, send_from, send_to, start_mode="mining"):
	target_price = stop_loss_price = mining_diff = None

	# Set current hour in times from epoch for 'mining hour'
	current_hour_in_seconds = round(time.time() - (round(time.time()%3600)))
	capi = CoinexAPI(access_id, secret_key)
	mining_diff = float(capi.get_mining_difficulty()['difficulty'])
	least_amount_allowed = float(capi.least_amount(market)['least_amount'])
	date = tradeutils.get_date()
	total_fees_in_CET = amount_to_add = 0
	file, filename = fileops.open_file(date)
	fileops.start_trading(file, date)
	email_not_sent = True


	while(1):

		# THIS ONLY WORKS WHEN THE FEE LIMIT HAS BEEN REACHED IN THE 9PM HOUR
		today, current_hour = tradeutils.get_time()

		if (current_hour) == 20 and email_not_sent:
			file.close()
			emailops.send_email(send_from, send_to, "Trade logs for {0}/{1}".format(today.month, today.day), "See attached for todays trade logs", [filename])
			email_not_sent = False
			date = tradeutils.get_date()
			file, filename = fileops.open_file(date)
			fileops.start_trading(file, date)


		while((total_fees_in_CET < mining_diff) and not (current_hour == 20 and email_not_sent)):
			try:
				# Get the current balance of the Token being traded in order to calculate the amount to be bought at a given price
				amount = float(capi.account_info()[market[3:]])
				# Get ticker data of market that we are trading in to get the current price
				market_ticker = capi.market_ticker(market)['ticker']
				# using the highest bid price, add a cent to get our current_price
				current_price = float(market_ticker['buy']) + swing_amount
				# calculate purchase_amount of Token to buy rounding to 8 decimal places
				purchase_amount = tradeutils.precise_round(amount/current_price,8)

				#### IOC Trade ####
				fileops.buy_placed(file, purchase_amount, market[:3])
				amount_bought, trade_data = tradeops.place_buy_order(capi, market, purchase_amount, current_price)

				if amount_bought == 0:
					continue
				
				fileops.buy_executed(file, amount_bought, market[:3], current_price, amount_bought*current_price, market[3:])
				cur_trade_time = tradeutils.get_date()
				fileops.time_trade_executed(file, cur_trade_time)
				trade_fees = float(trade_data['deal_fee'])
				stop_loss_price = float(trade_data['avg_price'])*0.9995
				stop_loss_sell_criteria = float(trade_data['avg_price'])*0.99955
				total_fees_in_CET += tradeops.get_fees(capi, market, trade_fees)

				# Get last price for the current market
				market_ticker = capi.market_ticker(market)['ticker']
				current_price = float(market_ticker['buy'])
				current_ask_price = float(market_ticker['sell'])
				target_price = float(market_ticker['sell'])-swing_amount
				fileops.buy_trade_stats(file, trade_fees, total_fees_in_CET, target_price, stop_loss_price)

				amount_bought = least_amount_allowed if amount_bought < least_amount_allowed else amount_bought
				# Make closing limit trade
				closing_trade = capi.limit_order(market, "sell", float(amount_bought+amount_to_add), target_price)
				#check status of limit order just placed
				closing_id = closing_trade['id']
				fileops.limit_sell_placed(file, closing_trade['amount'], market[:3], target_price, float(closing_trade['amount'])*target_price, market[3:])
		
				closing_trade_status = "not_deal"
				while(closing_trade_status != "done" and (current_price > stop_loss_price or current_ask_price > stop_loss_sell_criteria)):
					#update prices
					market_ticker = capi.market_ticker(market)['ticker']
					current_ask_price = float(market_ticker['sell'])
					current_price = float(market_ticker['buy'])
					status_resp = capi.order_status(closing_id, market)
					# unex = capi.unex_list(1,market,10)
					if status_resp != "status":
						closing_trade_status = status_resp['status']
				# if the stop loss kicked in close out trade with market sell
				if closing_trade_status != "done":
					stop_loss_resp, amount_to_add = tradeops.stop_loss_trade(capi, closing_id, market, least_amount_allowed)
					if stop_loss_resp:
						fileops.market_sell_executed(file, stop_loss_resp['deal_amount'], market[:3], stop_loss_resp['avg_price'], stop_loss_resp['deal_money'], market[3:])
						if closing_order['amount'] != stop_loss_resp['amount']:
							fileops.limit_sell_executed(file, (float(closing_trade['amount'])-float(stop_loss_resp['amount'])), market[:3], target_price, (float(closing_trade['amount'])-float(stop_loss_resp['amount']))*target_price, market[3:])

				closed_trade = capi.executed_list(1,market,10)[0]
				market_ticker = capi.market_ticker("CET{0}".format(market[3:]))
				trade_fees_for_closing_trade = float(closed_trade['deal_fee'])/float(market_ticker['ticker']['last'])
				total_fees_in_CET += trade_fees_for_closing_trade
				fileops.sell_trade_stats(file, trade_fees_for_closing_trade, total_fees_in_CET)
				fileops.end_trade(file)
				
				
				today, current_hour = tradeutils.get_time()
				if current_hour == 21:
					email_not_sent = True

				#Check for new hour started
				if time.time() - current_hour_in_seconds > 3600:
					# Check mining difficult
					mining_diff = float(capi.get_mining_difficulty()['difficulty'])
					fileops.hour_fees(file, current_hour_in_seconds, total_fees_in_CET)
					current_hour_in_seconds += 3600
					total_fees_in_CET = 0
			except KeyError as e:
				fileops.error(file, e)
				time.sleep(1)
		# passed amount of fees allowed for the hour
		# sleep program for remainder of hour		
		sleeptime = tradeutils.sleep_for_remaining_time_in_hour(current_hour_in_seconds)
		fileops.slept(sleeptime)
		current_hour_in_seconds += 3600
		total_fees_in_CET = 0


def main(argv):
	access_id = secret_key = None
	try:
		opts, args = getopt.getopt(argv,"ha:s:",["help","access_id","secret_key"])
	except getopt.GetoptError:
		print ('Invalid Option. Use -h or --help for command line syntax')
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print('\n\nSYNTAX\n\nAlgo.py -a <access_id> -s <secret_key> \n')
			print('OPTIONS\n\n-a --access_id\t This is the access_id taken from your Coinex API.\n')
			print('-s --secret_key\t This is the secret_key taken from your Coinex API.\n')
			sys.exit()
		elif opt in ('-a','--access_id'):
			access_id = arg
		elif opt in ('-s','--secret_key'):
			secret_key = arg
		else:
			print("{0} is not a valid option").format(opt)

	start(access_id, secret_key, "CETUSDT", 0.00003, 0.000001, "ENTER_EMAIL@HERE.com", ["ENTER_RECIPIENT_EMAIL@HERE.com"])

if __name__ == "__main__":
	main(sys.argv[1:])
#!/usr/bin/env python
