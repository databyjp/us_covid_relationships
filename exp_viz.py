# ========== (c) JP Hwang 16/5/20  ==========

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
import plotly.express as px

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

df = pd.read_csv('output/merged_covid_df.csv', index_col=0)
df = df.assign(cases_percap=df['cases']/df['POP_ESTIMATE_2018'])


df = df.assign(income_bins = pd.qcut(df['Median_Household_Income_2018'], 4))
fig = px.scatter(df, x='POP_ESTIMATE_2018', y='cases', color='cases_percap', color_continuous_scale=px.colors.sequential.Greens,
                 facet_col='income_bins', facet_col_wrap=1,
                 log_x=True, log_y=True)
fig.show()



df = df.assign(pov_bins = pd.qcut(df['PCTPOVALL_2018'], 4))
fig = px.scatter(df, x='POP_ESTIMATE_2018', y='cases_percap', color='PCTPOVALL_2018', color_continuous_scale=px.colors.sequential.Greens,
                 facet_col='pov_bins', facet_col_wrap=1,
                 log_x=True, log_y=True)
fig.show()


df = df[df['Rural-urban_Continuum Code_2013'].notna()]
df = df.assign(urban_bins = pd.qcut(df['Rural-urban_Continuum Code_2013'], 4))
df['Rural-urban_Continuum Code_2013'] = df['Rural-urban_Continuum Code_2013'].astype(str) + ' '
fig = px.scatter(df, x='POP_ESTIMATE_2018', y='cases_percap', color='Rural-urban_Continuum Code_2013', color_continuous_scale=px.colors.sequential.Greens,
                 facet_col='urban_bins', facet_col_wrap=1,
                 log_x=True, log_y=True)
fig.show()
