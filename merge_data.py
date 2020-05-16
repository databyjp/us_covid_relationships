# ========== (c) JP Hwang 13/5/20  ==========

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

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

# ===== Load COVID data =====
covid_df = pd.read_csv('output/covid_df.csv', index_col=0)

# ===== Deal with missing data =====
covid_df = covid_df[covid_df.county != 'Unknown']
# NYT treats NYC as just one area - so we need FIPS for all of them
nyc_fips = [int(i) for i in ['36005', '36047', '36061', '36081', '36085']]
# NYT data is missing fips code for KC
kc_fip = int('38000')

covid_df.loc[covid_df.county == 'Kansas City', 'fips'] = kc_fip
covid_df.fips = covid_df.fips.fillna(0).astype(int)

# ===== LOAD & PROCESS POPULATION DATA =====
pop_df = pd.read_csv('srcdata/PopulationEstimates.csv', encoding='latin1')
pop_df = pop_df[pop_df['FIPS'].notna()]
pop_df['fips'] = pop_df.FIPS.astype(int)
pop_keys = ['fips', 'State', 'Area_Name', 'Rural-urban_Continuum Code_2013', 'Urban_Influence_Code_2013', 'POP_ESTIMATE_2018']
pop_df = pop_df[pop_keys]

# Clean data
pop_df['POP_ESTIMATE_2018'] = pop_df['POP_ESTIMATE_2018'].fillna('0').str.replace('[$,]', '', regex=True).astype(int)

# ===== LOAD & PROCESS POVERTY DATA =====
pov_df = pd.read_csv('srcdata/PovertyEstimates.csv', encoding='latin1')
pov_df = pov_df[pov_df['FIPStxt'].notna()]
pov_df['fips'] = pov_df.FIPStxt.astype(int)
pov_keys = ['fips', 'Area_name', 'PCTPOVALL_2018']
pov_df = pov_df[pov_keys]

# ===== LOAD & PROCESS EMPLOYMENT DATA =====
emp_df = pd.read_csv('srcdata/Unemployment.csv', encoding='latin1')
emp_df = emp_df[emp_df['FIPS'].notna()]
emp_df['fips'] = emp_df.FIPS.astype(int)
emp_keys = ['fips', 'State', 'Area_name', 'Unemployment_rate_2018', 'Median_Household_Income_2018']
emp_df = emp_df[emp_keys]

# Clean data
emp_df['Median_Household_Income_2018'] = emp_df['Median_Household_Income_2018'].fillna('0').str.replace('[$,]', '', regex=True).astype(int)

# ================================
# ========== MERGE DATA ==========
# ================================

# Get latest data
cur_covid_df = covid_df[covid_df.date == covid_df.date.max()]

for (data_col, tmp_df) in [
    ('Rural-urban_Continuum Code_2013', pop_df), ('Urban_Influence_Code_2013', pop_df), ('POP_ESTIMATE_2018', pop_df),
    ('PCTPOVALL_2018', pov_df),
    ('Unemployment_rate_2018', emp_df), ('Median_Household_Income_2018', emp_df)
]:
    cur_covid_df.loc[:, data_col] = 0
    for i, row in cur_covid_df.iterrows():
        cur_fips = row['fips']
        tmp_vals = tmp_df[tmp_df.fips == cur_fips][data_col].values

        if row['county'] != 'New York City':
            cur_covid_df.loc[i, data_col] = tmp_vals[0]
        else:
            cur_covid_df.loc[i, data_col] = sum(tmp_vals)

cur_covid_df.to_csv('output/merged_covid_df.csv')
