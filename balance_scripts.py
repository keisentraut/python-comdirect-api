import pandas as pd
from create_dataframe import get_df

def balance_transactions(outputdir,currenttime):
	header = ['bookingDate','remittanceInfo','amount.value','transactionType.key']
	newheader = ['Date','WKN','Netto','Type']
	df3 = get_df("balance_transactions", header, newheader, outputdir,currenttime)
	return df3
