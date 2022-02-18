#!/usr/bin/env python
# coding: utf-8

# In[15]:


import pandas as pd
import os
import glob
import numpy as np
import datetime
import pandas as pd
import seaborn as sb
from matplotlib import pyplot as plt
import pickle
# Import Statsmodels
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.eval_measures import rmse, aic
from statsmodels.tsa.vector_ar.vecm import coint_johansen

# In[49]:


interpolate_df=pd.read_csv("./Data/Interpolate_24.csv")
try:
    interpolate_df.drop(['Unnamed: 0'],axis=1,inplace=True)
    interpolate_df.drop(['MOL_VFD_-2_OUT'],axis=1,inplace=True)
except Exception as e:
    print(e)


print("Training data Shape : ",interpolate_df.shape)
print("Trianing Data Head ",interpolate_df.head(3))
print("Training Data Info ",interpolate_df.info())
print("Training Data Stats ",interpolate_df.describe().T)

interpolate_df.rename({'MILK OF LIME BAUME': 'MILK_F_LIME_BAUME', 'MOL_VFD_-1_OUT': 'MOL_VFD_1_OUT'}, axis=1, inplace=True)
interpolate_df = interpolate_df.replace(to_replace =["Pt Created", "Configure","I/O Timeout","Bad","Under Range","Over Range","Scan Off","Digital State"],value = 0)
SOCK_PH_threshold={"Model_9.1":[9.06,9.15],"Model_8.1":[8.06,8.12]}

for th in SOCK_PH_threshold:
    result_filtered = interpolate_df.query("MILK_F_LIME_BAUME > 6 and MILK_F_LIME_BAUME < 10")
    result_filtered = result_filtered.query("MILK_OF_LM_FL > 6 and MILK_OF_LM_FL < 25")
    result_filtered = result_filtered.query("MIX_JUICE_BRIX > 12.85 and MIX_JUICE_BRIX < 13.25")
    result_filtered = result_filtered.query("MIX_JUICE_FL > 450 and MIX_JUICE_FL < 550")
    result_filtered = result_filtered.query("MIX_JUICE_PH > 4.5 and MIX_JUICE_PH < 6")
    # result_filtered = result_filtered.query("MOL_VFD_-2_OUT > 8.5 and MOL_VFD_-2_OUT < 9.5")
    result_filtered = result_filtered.query("MOL_VFD_1_OUT > 40 and MOL_VFD_1_OUT < 85")

    result_filtered = result_filtered.query("SOCK_PH > {} and SOCK_PH < {}".format(str(SOCK_PH_threshold[th][0]),str(SOCK_PH_threshold[th][1])))
    # result_filtered.to_csv("Interpolate_filtered_24.csv")
    i_file=result_filtered.columns[1:]
    i_file
    result_filtered.set_index('Timestamp',inplace=True)


    def cointegration_test(df, alpha=0.05): 
        """Perform Johanson's Cointegration Test and Report Summary"""
        out = coint_johansen(df,-1,5)
        d = {'0.90':0, '0.95':1, '0.99':2}
        traces = out.lr1
        cvts = out.cvt[:, d[str(1-alpha)]]
        def adjust(val, length= 6): return str(val).ljust(length)

        # Summary
        print('Name   ::  Test Stat > C(95%)    =>   Signif  \n', '--'*20)
        for col, trace, cvt in zip(df.columns, traces, cvts):
            print(adjust(col), ':: ', adjust(round(trace,2), 9), ">", adjust(cvt, 8), ' =>  ' , trace > cvt)

    cointegration_test(result_filtered)

    nobs = 52
    df_train, df_test = result_filtered[0:-nobs], result_filtered[-nobs:]

    # Check size
    print(df_train.shape)  
    print(df_test.shape)  
#model training
    model = VAR(df_train)
    x = model.select_order(maxlags=1)
    print("Model Summary",x.summary())
    model_fitted = model.fit(1)

     
    # Save the trained model as a pickle string.
    pickle.dump(model_fitted, open('DCM_{}.pkl'.format(th), 'wb'))
