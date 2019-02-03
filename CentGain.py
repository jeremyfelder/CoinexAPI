from CoinexAPI import CoinexAPI
import time

market = "CETUSDT"
capi = CoinexAPI("35723FF964944EE9BF47E36F276A7245","84B87FE2247A4930AB9D5DA011C8F9DB559C9C225E404674")
market_ticker = capi.market_ticker(market)
ticker_data = market_ticker['ticker']

buy_price = float(ticker_data['buy'])
sell_price = float(ticker_data['sell'])
spread = sell_price - buy_price

start_time = time.time()
amount_to_sell = 100
sell_order = capi.limit_order(market, "sell", amount_to_sell, sell_price)
print("Sell order of {0} {1} at {2} took {3} seconds".format(amount_to_sell , "CET", sell_price, time.time()-start_time))

trade_id = int(sell_order['id'])
order_status = capi.order_status(trade_id, market)
while (order_status['status'] != "done"):
	time.sleep(0.053)
	order_status = capi.order_status(trade_id, market)

buy_price = sell_price-0.000001
amount_to_buy = order_status['deal_amount']
start_time = time.time()
buy_order = capi.limit_order(market, "buy", amount_to_buy, buy_price)
print("Buy order of {0} {1} at {2} took {3} seconds".format(amount_to_buy, "CET", buy_price, time.time()-start_time))
