from datetime import datetime
import time


def open_file(date):
	filename = "logs/{0}/{1}/{2}.txt".format(date.strftime("%B"), date.strftime("%d"), date.strftime("%I%M"))
	file = open(filename, 'a')
	return file, filename


def start_trading(file, date):
	file.write("Trading started at: {0}\n".format(date.strftime("%A, %B %d,  %Y %I:%M:%S")))

# Buy functions

def buy_placed(file, amount, market):
	file.write("Placing order for {0} {1}\n".format(amount, market))


def buy_executed(file, amount_bought, pair, current_price, cost, pair2):
	file.write("Buy order of {0} {1} executed at {2} for {3} {4}\n".format(amount_bought, pair, current_price, cost, pair2))


# def market_buy_executed(file):


def time_trade_executed(file, cur_trade_time):
	file.write("Trade executed at: {0}\n".format(cur_trade_time.strftime("%A, %B %d,  %Y %I:%M:%S")))

# Trade Stats functions
def buy_trade_stats(file, trade_fee, total_current_fees, target_price, stop_loss_price):
	file.write("Stats set:\nTrade Fee: {0}\nTotal Trade Fees: {1}\nTarget Price: {2}\nStop Loss Price: {3}\n".format(trade_fee, total_current_fees, target_price, stop_loss_price))


def sell_trade_stats(file, trade_fees, total_fees):
	file.write("Stats set:\nTrade Fee: {0}\nTotal Trade Fees: {1}\n".format(trade_fees, total_fees))


# Sell functions
def limit_sell_placed(file, closing_amount, pair, target_price, potential_cost, pair2):
	file.write("Sell order of {0} {1} placed at {2} for {3} {4}\n".format(closing_amount, pair, target_price, potential_cost, pair2))


def limit_sell_executed(file, closing_amount, pair, target_price, closing_cost, pair2):
	file.write("Sell order of {0} {1} executed at {2} for {3} {4}\n".format(closing_amount, pair, target_price, closing_cost, pair2))


#def ioc_sell_executed(file):


def market_sell_executed(file, closing_amount, pair, avg_price, closing_cost, pair2):
	file.write("Market Sell of {0} {1} executed at {2} for {3} {4}\n".format(closing_amount, pair, avg_price, closing_cost, pair2))


def hour_fees(file, cur_hour_in_secs, total_fees):
	file.write("Hour of: {0} had {1} fees in CET\n".format(cur_hour_in_secs, total_fees))

def slept(file, time_slept):
	file.write("Program slept for: {0}\n".format(time_slept))

# End Trade
def end_trade(file):
	file.write("*************** End Trade ***************\n")
	file.flush()


def error(file, e):
	file.write("{0}\n".format(e))

