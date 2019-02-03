from datetime import datetime 
import time


def precise_round(amount, num_decimals):
	num_as_string = str(amount)
	whole_and_decimal = num_as_string.split(".")
	rounded_string = whole_and_decimal[0] + "." + whole_and_decimal[1][:num_decimals]
	return float(rounded_string)


def get_date():
	date = datetime.fromtimestamp(time.time()-14400)
	return date


def get_time():
	today = datetime.today()
	current_hour = today.hour-4
	return today, current_hour


def sleep_for_remaining_time_in_hour(current_hour_in_seconds):
		next_hour_seconds = current_hour_in_seconds + 3600
		sleeptime = round(next_hour_seconds-time.time(), 2)
		time.sleep(sleeptime)
		return sleeptime