# -*- coding: utf-8 -*-
"""
Created on Tue May 18 13:16:38 2021

@author: s792
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import json

r = requests.get('http://opendata.ffe.de:3000/v_opendata?id_opendata=eq.5')
r_dict = json.loads(r.content)
# df = pd.read_json(result.content)
data_content = r_dict[0]['data']
data_df = pd.DataFrame(data_content)
data_df.set_index('region', inplace=True)  
data_series = data_df['values']
df = pd.DataFrame.from_dict(dict(zip(data_series.index, data_series.values)))
year = data_df.year_weather.unique()[0]
dti = pd.date_range(start='1/1/'+str(year), end='1/1/'+str(year+1), closed='left', 
                    freq='H', tz='Europe/Brussels')
df.index = dti
