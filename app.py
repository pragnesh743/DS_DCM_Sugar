#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import time
import json
import config
import logging
import numpy as np
import pickle
import base64
import datetime
import pandas as pd
from pi_server_connection import ConnectionPI
import statsmodels.api as sm
import statsmodels.formula.api as smf





# In[2]:

model_path=config.MODEL_PATH
STATEMATRIX_PATH=config.STATEMATRIX_PATH

# Get current file name
# cur_file_name = os.path.basename(__file__)
cur_file_name = os.path.basename("DASH_APP")


# Logger Initialization
logging.getLogger(__name__)
logging.basicConfig(filename=config.LOGGER_PATH,level=logging.DEBUG , filemode='a', format='%(name)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)


# In[3]:


class SUGAR_PH():
    def __init__(self,input_dataframe):
        global STATEMATRIX_PATH
        print("Main Forcasting process started",STATEMATRIX_PATH)
        logging.info('Class Initialization | Time '+str(time.time())+'')
        
        starttime = time.time()
        # State matrix for infer the data
        self.sugar_dataset = pd.read_csv(STATEMATRIX_PATH)  
        self.state_matrix = self.sugar_dataset.filter(['MILK_F_LIME_BAUME',
                                              'MILK_OF_LM_FL', 
                                              'MIX_JUICE_BRIX',
                                               'MIX_JUICE_FL', 
                                               'MIX_JUICE_PH',
                                                'MOL_VFD_1_OUT',
                                                 'SOCK_PH' ])  

#         self.input_dataframe=pd.read_csv("testing_df.csv")

        self.input_dataframe=input_dataframe[:12]
#         self.input_dataframe.set_index('Timestamp',inplace=True)
#        input_dataframe=pd.read_csv("test_input.csv")

        self.input_value_dataframe = self.input_dataframe.filter([
                                                                 'MILK_F_LIME_BAUME',
                                                                  'MILK_OF_LM_FL', 
                                                                  'MIX_JUICE_BRIX',
                                                               'MIX_JUICE_FL', 
                                                               'MIX_JUICE_PH',
                                                                'MOL_VFD_1_OUT',
                                                                 'SOCK_PH' ])

        self.test_data1 = self.input_value_dataframe
        self.dataT = self.test_data1.to_numpy()
#        print(dataT)
        endtime=time.time() - starttime
        


    def adaptation(self,s_index,e_index):
        """
            Adaptation concept is used to stop the deviation of the generated prediction from the required prediction range  
            The actual value adapts the MAX and MIN of the state matrix
        """
        logging.info("adaptation process started" +str(time.time())+'')
        try:
#            index=0
            
#            for index in range(s_index,e_index):
            print("#"*8,"in apdation ","#"*8)
            self.dataT = self.test_data1.to_numpy()
            # print(dataT)
#            rowval = self.test_data1
##            print(rowval.T)            
            state_len =self.state_matrix.columns
            test_data_len = self.test_data1.columns

            if len(state_len) == len(test_data_len):
#                    actual_val = self.test_data1.iloc[[index]]
#                    columns_name=self.test_data1.columns
                for col_pos in range(len(state_len)):
#                        print(col_pos,test_data_len[col_pos])
                    # get values of a particular column from statematrix
#                    adaptation = self.state_matrix.dropna().iloc[:,[col_pos]]

                    adapt_min = [self.state_matrix.loc[0][test_data_len[col_pos]]]
                    adapt_max = [self.state_matrix.loc[1][test_data_len[col_pos]]]
#                     print(col_pos,test_data_len[col_pos])

                    self.test_data1.loc[self.test_data1[test_data_len[col_pos]] <=adapt_min[0], test_data_len[col_pos]] = adapt_min[0]
                    self.test_data1.loc[self.test_data1[test_data_len[col_pos]] >= adapt_max[0], test_data_len[col_pos]] = adapt_max[0]

        # import pdb; pdb.set_trace()

            return self.test_data1
        except Exception as ex:
            # Log error 
            print(ex)
            config.error_logger(ex,cur_file_name)
    def infer(self,Inputdf):
        print("#"*8,"in infer ","#"*8)
        print("model_path in infer",model_path)
        logging.info("Model infer started" +str(time.time())+'')
        # print(Inputdf)
        model_fitted = pickle.load(open(config.MODEL_PATH, 'rb'))
        # print(loaded_model.summary())
        lag_order = model_fitted.k_ar
        # print(lag_order)  #> 4
        forecast_input = Inputdf[-12:].values
        print("Forecasting Input \n")
        print(forecast_input)
        nobs=5
        fc = model_fitted.forecast(y=forecast_input, steps=nobs)
        
#         print(fc)
        df_forecast = pd.DataFrame(fc, index=Inputdf.index[-nobs:], columns=Inputdf.columns )
        df_forecast.rename(columns = {'MILK_F_LIME_BAUME':'PRED MILK OF LIME FLOW',
                                'MILK_OF_LM_FL':'PRED MILK OF LIME FLOW',
                                'MIX_JUICE_BRIX':'PRED MIX JUICE BRIX',
                                'MIX_JUICE_FL':'PRED MIX JUICE FLOW',
                                'MIX_JUICE_PH':'PRED MIX JUICE PH',
                                'MOL_VFD_1_OUT':'PRED MOL VFD -1 OUTPUT',
                                'SOCK_PH':'PRED SOCK PH' }, inplace = True)
# PRED MILK OF LIME BAUME PRED MILK OF LIME FLOW  PRED MIX JUICE BRIX PRED MIX JUICE FLOW PRED MIX JUICE PH   PRED MOL VFD -1 OUTPUT  PRED SOCK PH
        predictions = df_forecast.to_numpy()
        predictions = predictions[0]
        print("#"*8,"OUT infer ","#"*8)

        return df_forecast
    def vbmAdapted(self,index):
        """
           Vector based modelling for generating the prediction.
           The input from pi server are collected and undergoes adaptation rule.
           Then it passes through a model 
           The predicted results gets updated to the server.
        """
        starttime = time.time()
        print("#"*8,"in vbmAdapted ","#"*8)

        try:
            s_index=0
            e_index=12
            # Adapted input values are returned from the adaptation function
            actual_data = self.adaptation(s_index,e_index)
#             print(actual_data)
            columnnames = actual_data.columns
            # dataT = actualData.to_numpy()
            print(columnnames)
            # rowval1 = dataT
            Inputdf=actual_data
            pred = self.infer(actual_data)
            predicteddataframe = pred
            # Update prediction to the server 
            self.pi_connector = ConnectionPI()
            idf,input_webid_timestamp =self.pi_connector.extract_input_data()
            print("\n"*2)
            print(predicteddataframe[:1],input_webid_timestamp)
            print("\n"*2)

            self.pi_connector.update_output_data(predicteddataframe[:1],input_webid_timestamp)
            print(10*"#","_OUTPUT_","#"*10)
            # print(predicteddataframe)
            endtime = time.time() - starttime
            logging.info('SOCK PH prediction done | Time :'+str(time.time())+'')
            return pred
        except Exception as ex:
            # Log error 
            print(ex)
            config.error_logger(ex,cur_file_name)


# In[4]:


def infer_from_class(df):
    try:    
        starttime = time.time()
        # create and instance for SUGAR_PH class
        logging.info("create and instance for SUGAR_PH class" +str(time.time())+'')
        carbon_density_detection_obj = SUGAR_PH(df)
        print('SUGAR_PH Class Initialization')
        logging.info('SUGAR_PH Class Initialization')
        endtime = time.time() - starttime
        print('Function Start Time',endtime)
        # Vector based modelling algorithm
        df_op=carbon_density_detection_obj.vbmAdapted(0)
#         print("output",df_op)
        endtime = time.time() - starttime
        print('TOTAL CODE EXECUTION TIME',endtime)
        logging.info('Total program execution time :'+str(endtime)+'')
        return df_op
    except Exception as ex:
        # Log error 
        print(ex)
        config.error_logger(ex,cur_file_name)


# In[5]:

def Data_log_read():
    data_path=config.DATA_PATH
    # input_dataframe=pd.read_csv("testing_df.csv")
            # Get data from PI Server
    try:
        logging.info('Connecting PI server In data log read:'+str(time.time())+'')
        pi_connector = ConnectionPI()
        input_value_dataframe,input_webid_timestamp = pi_connector.extract_input_data()
        # input_webid_timestamp.to_csv("apc.csv")
        # print(input_value_dataframe,input_webid_timestamp)
        # input_dataframe.rename({'MILK OF LIME BAUME': 'MILK_F_LIME_BAUME', 'MOL_VFD_-1_OUT': 'MOL_VFD_1_OUT'}, axis=1, inplace=True)
        # MILK OF LIME BAUME  MILK_OF_LM_FL   MIX_JUICE_BRIX  MIX_JUICE_FL    MIX_JUICE_PH    MOL_VFD_-1_OUT  SOCK_PH
        ###207 
        # ['MILK OF LIME BAUME',
        #                                         'MILK OF LIME FLOW',
        #                                         'MIX JUICE BRIX',
        #                                         'MIX JUICE FLOW',
        #                                         'MIX JUICE PH',
        #                                         'MOL VFD -1 OUTPUT',
        #                                         'SOCK PH' ]
        if config.SERVER=="DEVELOPMENT":
            input_value_dataframe.rename(columns = {'MILK OF LIME BAUME':'MILK_F_LIME_BAUME',
                                            'MILK OF LIME FLOW':'MILK_OF_LM_FL',
                                            'MIX JUICE BRIX':'MIX_JUICE_BRIX',
                                            'MIX JUICE FLOW':'MIX_JUICE_FL',
                                            'MIX JUICE PH':'MIX_JUICE_PH',
                                            'MOL VFD -1 OUTPUT':'MOL_VFD_1_OUT',
                                            'SOCK PH':'SOCK_PH' }, inplace = True)   
        else: 
            input_value_dataframe.rename(columns = {'MILK OF LIME BAUME':'MILK_F_LIME_BAUME',
                                            'MILK_OF_LM_FL':'MILK_OF_LM_FL',
                                            'MIX_JUICE_BRIX':'MIX_JUICE_BRIX',
                                            'MIX_JUICE_FL':'MIX_JUICE_FL',
                                            'MIX_JUICE_PH':'MIX_JUICE_PH',
                                            'MOL_VFD_-1_OUT':'MOL_VFD_1_OUT',
                                            'SOCK_PH':'SOCK_PH' }, inplace = True)
        input_value_dataframe = input_value_dataframe.filter([
                                                     'MILK_F_LIME_BAUME',
                                                      'MILK_OF_LM_FL', 
                                                      'MIX_JUICE_BRIX',
                                                       'MIX_JUICE_FL', 
                                                       'MIX_JUICE_PH',
                                                        'MOL_VFD_1_OUT',
                                                         'SOCK_PH' ])
        input_value_dataframe['Timestamp']=datetime.datetime.strftime(pd.Timestamp.now(), '%Y-%m-%d %H:%M:%S')
        # print(input_value_dataframe)
        input_dataframe_read=pd.read_csv(data_path)
        input_dataframe_read = input_dataframe_read.filter(['Timestamp',
                                                     'MILK_F_LIME_BAUME',
                                                      'MILK_OF_LM_FL', 
                                                      'MIX_JUICE_BRIX',
                                                       'MIX_JUICE_FL', 
                                                       'MIX_JUICE_PH',
                                                        'MOL_VFD_1_OUT',
                                                         'SOCK_PH' ])
        # datetime.datetime.strftime(pd.Timestamp.now(), '%Y-%m-%d %H:%M:%S')
        pd.concat([input_dataframe_read, input_value_dataframe])[1:].to_csv(data_path)
        # print(input_dataframe_read)
    except Exception as ex:
        config.error_logger(ex,cur_file_name)
    
    df=pd.read_csv(data_path)
    # # input_dataframe.set_index('Timestamp',inplace=True)
    # # df=input_dataframe[-24*60*60:]
    # df=input_dataframe_read.copy()
    logging.info('Data Log Read Process Completed'+str(time.time())+'')
    df=df.reset_index()
    return df
# df=Data_log_read()
if __name__ == '__main__':
    while 1:
        df=Data_log_read()
        # print("Input data",df)
        infer_from_class(df)
        logging.info("All Preocess Completed"+str(time.time())+'')