import datetime
from depot_scripts import depot_transactions, depot_positions
from balance_scripts import balance_transactions
from requests import main_requests

def currenttime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

def start():
	#Personal Information
	client_id=input("Please enter client_id: ")
	client_secret=input("Please enter client_secret: ")
	username = input("Please enter username: ")
	password = input("Please enter password: ")
	min_transactiondate = input(raw_input("Please enter START of transaction date (otherwise press enter): ") or currenttime()[:4]"-01-01")
	max_transactiondate = input(raw_input("Please enter END of transaction date (otherwise press enter): ") or currenttime())
	main_requests(client_id, client_secret, username, password)

	#Get data in dataframe for analysis
	df1 = depot_positions()
	df2 = depot_transactions()
	df3 = balance_transactions()


if __name__ == "__main__":
	start()
