import datetime
import sys, os
from depot_scripts import depot_transactions, depot_positions
from balance_scripts import balance_transactions
from request_script import main_requests

def currenttime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

def start():
	currentdir=sys.argv[1]
	currentdir=currentdir.replace("\\","/")
	if not os.path.exists('Output'):
    		os.makedirs('Output')
	currentdir = currentdir+'/Output'
	#Personal Information
	client_id=input("Please enter client_id: ")
	client_secret=input("Please enter client_secret: ")
	username = input("Please enter username: ")
	password = input("Please enter password: ")
	
	#Comdirect has NOT implemented this!
	min_transactiondate = input("Please enter START of transaction date (otherwise press enter): ") or currenttime()[:4]"-01-01"
	max_transactiondate = input("Please enter END of transaction date (otherwise press enter): ") or currenttime()
	
	#Get requests calls and several files are saved for further investigation
	main_requests(client_id, client_secret, username, password, min_transactiondate, max_transactiondate, currentdir)

	#Get data in dataframe for analysis
	df1 = depot_positions()
	df2 = depot_transactions()
	df3 = balance_transactions()
	
	#Export dataframes to excel
	df1.to_excel(currentdir+'/'+"depot_positions"+currenttime+".xlsx")
	df2.to_excel(currentdir+'/'+"depot_transactions"+currenttime+".xlsx")
	df3.to_excel(currentdir+'/'+"balance_transactions"+currenttime+".xlsx")


if __name__ == "__main__":
	start()
