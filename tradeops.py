from CoinexAPI import CoinexAPI
import time


def get_fees(capi, market, trade_fees):
	if market[:3] != "CET":
		market_ticker = capi.market_ticker("CET{0}".format(market[:3]))
		trade_fees = (trade_fees/float(market_ticker['ticker']['last']))
	return trade_fees


def place_buy_order(capi, market, purchase_amount, current_price):
	trade_data = capi.ioc_order(market, "buy", purchase_amount, current_price)
	try:
		amount_bought = float(trade_data['deal_amount'])
	except KeyError:
		ordertype = "not_buy"
		while(ordertype != "buy"):
			time.sleep(1)
			last_executed_order = capi.executed_list(1, market, 20)[0]
			ordertype = last_executed_order['type']
		if precise_round(float(last_executed_order['amount']), 8) == purchase_amount:
			min_amount_allowed_to_buy = float(capi.least_amount(market)['least_amount'])
			last_executed_amount = float(last_executed_order['deal_amount'])
			amount_bought = last_executed_amount if last_executed_amount > min_amount_allowed_to_buy else min_amount_allowed_to_buy
		else:
			amount_bought = 0
		trade_data = last_executed_order
	return amount_bought, trade_data


def stop_loss_trade(capi, closing_id, market, least_amount_allowed):
	response = {}
	amount_to_add = 0
	cancel_previous_limit = capi.cancel_order(closing_id, market)
	if cancel_previous_limit != "pending":
		amount_to_close = float(cancel_previous_limit['amount']) - float(cancel_previous_limit['deal_amount']) 
		if amount_to_close > least_amount_allowed:
			response = capi.market_order(market, 'sell', amount_to_close)
		else:
			amount_to_add = amount_to_close
	return response, amount_to_add