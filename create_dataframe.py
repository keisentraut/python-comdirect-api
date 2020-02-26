import pandas as pd
import json
from pandas.io.json import json_normalize

def get_df(file,header,newheader):
	with open(file) as f:
		data = json.load(f)
	tmp = json_normalize(data)
	tmp = tmp[['values']]
	tmp.columns = ['Werte']
	df = json_normalize(tmp.Werte[0])
	df = df[header]
	df.columns = newheader
	df['Date'] = pd.to_datetime(df['Date'])
	return df
