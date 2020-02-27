import pandas as pd
import json
from pandas.io.json import json_normalize

def get_df(file,header,newheader,outputdir,currenttime):
	with open(outputdir+'/'+file+'.json') as f:
		data = json.load(f)
	tmp = json_normalize(data)
	tmp = tmp[['values']]
	tmp.columns = ['Werte']
	df = json_normalize(tmp.Werte[0])
	df = df[header]
	df.columns = newheader
	df.to_excel(outputdir+'/'+file+'_'+currenttime+'.xlsx',index=False)
	df['Date'] = pd.to_datetime(df['Date']).dt.date
	return df
