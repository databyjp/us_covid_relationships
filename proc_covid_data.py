# ========== (c) JP Hwang 12/5/20  ==========

import logging

# ===== START LOGGER =====
logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
root_logger.addHandler(sh)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

"""
This is to read through the data files and concatenate data along each FIPS entry, 
which will form the basis of our analysis

Pseudocode:
- Read NYT COVID CSV file (contains NYT-collected COVID data)
- Determine what our Y-values will be, and process to find this value
    - Number of days with R > 1, before it comes back down?
    - Peak no. of daily infections
"""

# Read NYT COVID CSV file (contains NYT-collected COVID data)
covid_df = pd.read_csv('srcdata/us-counties.csv')

# See which FIPS numbers are missing
# print(covid_df[covid_df.fips.isna()].county.unique())
# New York City' 'Unknown' 'Kansas City']
# Following discussion here https://github.com/nytimes/covid-19-data/issues/105
for k, v in {'New York City': 0, 'Kansas City': 1}.items():
    mask = (covid_df['county'] == k)
    covid_df['fips'] = covid_df['fips'].mask(mask, covid_df['fips'].fillna(v))

# # A smaller dataset for testing
# covid_df = covid_df[covid_df['county'].isin(['Cook', 'New York City', 'Los Angeles'])]

# Create new columns for processing
covid_df = covid_df.assign(delta=0)
covid_df = covid_df.assign(delta_3day_ra=0)
covid_df = covid_df.assign(r=0)
covid_df = covid_df.assign(r_3day_ra=0)
covid_df = covid_df.assign(cases_3day_ra=0)
covid_df = covid_df.assign(datetime=pd.to_datetime(covid_df.date))

for i, row in covid_df.iterrows():
    today = datetime.fromisoformat(row['date'])
    today_minus1 = datetime.fromisoformat(row['date']) - timedelta(days=1)
    today_minus3 = datetime.fromisoformat(row['date']) - timedelta(days=3)
    prev_1day_row = covid_df[(covid_df['datetime'] == today_minus1) & (covid_df['fips'] == row['fips'])]
    prev_3days_rows = covid_df[(covid_df['datetime'] <= today) & (covid_df['datetime'] > today_minus3) & (covid_df['fips'] == row['fips'])]
    if len(prev_1day_row) > 0:
        prev_row = prev_1day_row.iloc[0]
        covid_df.loc[i, 'delta'] = row['cases'] - prev_row['cases']
        covid_df.loc[i, 'delta_3day_ra'] = row['cases_3day_ra'] - prev_row['cases_3day_ra']
        if len(prev_3days_rows) > 0:
            covid_df.loc[i, 'cases_3day_ra'] = prev_3days_rows['cases'].sum()/3
        if prev_row['delta'] > 0:
            covid_df.loc[i, 'r'] = row['delta'] / prev_row['delta']
            covid_df.loc[i, 'r_3day_ra'] = row['delta_3day_ra'] / prev_row['delta_3day_ra']
    else:
        covid_df.loc[i, 'delta'] = 0
    if (i+1) % 5000 == 0:
        logger.info(f'Processed {i+1} files')


# import plotly.express as px
# fig = px.bar(covid_df[['datetime', 'county', 'delta', 'delta_3day_ra']].melt(id_vars=['county', 'datetime']),
#              x='datetime', y='value', color='variable', facet_row='county', template='plotly_white', barmode='group')
# fig.show()

covid_df.to_csv('output/covid_df.csv')
