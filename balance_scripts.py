import pandas as pd
from create_dataframe import get_df

def balance_transactions(outputdir,currenttime):
	header = ['bookingDate','remittanceInfo','amount.value','transactionType.key']
	newheader = ['Date','WKN','Netto','Type']
	df3 = get_df("balance_transactions", header, newheader, outputdir,currenttime)
	df3 = df3[df3.Type == 'INTEREST_DIVIDENDS'][['Date','WKN','Netto']]
	df3['Brutto'] = df3.WKN.str.split('05').str[1].str.split(' ').str[2].str.replace(',','.').astype('float')
	df3.WKN = df3.WKN.str.split('03').str[1].str.split('04').str[1].str.split(' ').str[0]
	return df3
