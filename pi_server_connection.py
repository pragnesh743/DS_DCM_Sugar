# CARBON ANODE DENSITY PREDICTION

######################################################

#  Project Name: CARBON ANODE DENSITY PREDICTION
#  File : main.py
#       Server connection and data extraction from the pi server and 
#       the values are being updated to the PI server through PI WEB API.
#  Version: 1.1.0

######################################################

import os
import json
import config
import requests
import pandas as pd

# Get current file name
cur_file_name = os.path.basename(__file__)


class ConnectionPI():


    def __init__(self) -> None:
        # pass

        self.url = config.URL
        self.username = config.USERNAME
        self.password = config.PASSWORD
        self.batch_url = config.BATCH_URL
        self.streamset_url = config.STREAMSET_URL
        self.get_request_url = config.GET_REQUEST_URL
        self.input_tag_path = config.IN_TAG_WEBID
        self.output_tag_path = config.OUT_TAG_WEBID
        # self.dataserver_url = ''



    # Check server connection
    def pi_connection(self,url,username, password):
        """
            Checks the connection with the server
        """
        try:
            if config.SERVER=="DEVELOPMENT":
                result = requests.get(url, auth=(self.username, self.password),verify=False)
                # result = requests.get(url, auth=(self.username, self.password),verify=False)
            else:
                headers = {'cache-control': "no-cache",}
                result = requests.get(url, headers=headers, timeout=5, verify=False)
            return result

        except Exception as ex:
            # Log error 
            
            config.error_logger(ex,cur_file_name)



    # Get the details of the output channels
    def output_channels(self, links_url):
        """
            using nameFilter all the tags with the Prefix = 'CALC' are filtered out 
        """

        try:

            prefix = 'CALC'
            asset_url = links_url+"?nameFilter={0}*".format(prefix)
            # Collects the tags from server 
            response_points = requests.get(asset_url, auth=(self.username, self.password), verify=False)

            model_input_webid_timestamp = {}

            #  Iterate through 'Items' from the response
            for point in response_points.json()['Items']:
                
                point_value = point['Links']

                # print(point['Name'])
                model_input_webid_timestamp[point['Name']] = []

                # Get the link for key 'Value' 
                value_url = point_value['Value']
                response_value = requests.get(value_url, auth=(self.username, self.password), verify=False)

                model_input_values = []
                

                for values in response_value.json():                     
                    if values == 'Timestamp':
                        # Append the corresponding WebId to the tag name
                        # model_input_webid_timestamp[point['Name']].append(response_value.json()[values])
                        model_input_webid_timestamp[point['Name']].append(point['WebId'])

            return model_input_webid_timestamp

        except Exception as ex:
            # Log error 
            config.error_logger(ex,cur_file_name)



    # Get tag names, web id and timestamp
    def input_tag_data_extraction(self):
        """
            Connect to the PI Server and get the dataserver name
            Extract data from the server
            Get tag name and coresponding webid for it.
        """

        try:
            # connect to server 
            result = self.pi_connection(self.url, self.username, self.password)
            dataserver_url = result.json()['Links']['DataServers']
            # connect to the dataserver
            response = requests.get(dataserver_url, auth=(self.username, self.password), verify=False)
            model_input_dictionary = {}
            # model_input_webid_timestamp = {}
            # print(result)

            name_list = []

            for res in response.json()['Items']:           
                
                if res['Name'] == 'OSIPISERVER03':
                    server_details = res['Links']

                    links_url = server_details['Points']

                    prefix = 'ACTL'
                    asset_url = links_url+"?nameFilter={0}*".format(prefix)

                    response_points = requests.get(asset_url, auth=(self.username, self.password), verify=False)

                    #  Get the output channels 

                    model_input_webid_timestamp = self.output_channels(links_url)

                    for point in response_points.json()['Items']:
                        
                        point_value = point['Links']

                        # print(point['Name'])
                        model_input_dictionary[point['Name']] = []
                        # model_input_webid_timestamp[point['Name']] = []


                        value_url = point_value['Value']
                        response_value = requests.get(value_url, auth=(self.username, self.password), verify=False)

                        model_input_values = []
                        

                        for values in response_value.json():
                            # if values == 'Value':
                            #     tag_values = response_value.json()[values]

                            #     if type(tag_values) is dict:                                
                            #         model_input_dictionary[point['Name']].append(tag_values['Value'])
                                    
                            #     elif  type(tag_values) is float:
                            #         model_input_dictionary[point['Name']].append(tag_values)
                            #     else:
                            #         pass                      
                            # Append webid with tagnames
                            if values == 'Timestamp':
                                # model_input_dictionary[point['Name']].append(response_value.json()[values])
                                model_input_dictionary[point['Name']].append(point['WebId'])
            
            # print(model_input_dictionary)

            # Create dataframe with the dictionary
            in_tags = pd.DataFrame(model_input_dictionary)
            out_tags = pd.DataFrame(model_input_webid_timestamp)
            # Sort the columnnames 
            in_tags = in_tags.reindex(sorted(in_tags.columns), axis=1)
            out_tags = out_tags.reindex(sorted(out_tags.columns), axis=1)
            # Save to csv
            in_tags.to_csv(config.IN_TAG_WEBID)
            out_tags.to_csv(config.OUT_TAG_WEBID)

            return 200
        except Exception as ex:
            # Log error 
            config.error_logger(ex,cur_file_name)



    # Sample test code
    def predicted_data(self, predicted_data,web_id,timestamp):
        try: 

            url = 'https://207.246.95.193/piwebapi/streams/{0}/recorded'.format(web_id)

            body = [{
            "Timestamp": timestamp,
            "UnitsAbbreviation": "",
            "Good": True,
            "Questionable": False,
            "Value": predicted_data
            }]

            # print(body)

            response = requests.post(url,json=body, verify=False)

        except Exception as ex:
            # Log error 
            config.error_logger(ex,cur_file_name)
        # r = requests.post(url, json=body, auth= self.username/self.password, headers = {'Content-Type': 'application/json', 'Accept':'application/json'} )
        return response.status_code



    # Get tag values using batch URL 
    def extract_input_data(self):
        """
            Read webid of each tag from the input_tag_path file,
            create a json request method and post the request using batch url
            Collect the vaules, timestamp to a dataframe and return 
        """
        try:    
            url = self.batch_url
            # get input tag webid from csv file
            input_dataframe = pd.read_csv(self.input_tag_path)
            columnnamelist = input_dataframe.columns.tolist()
            webids = input_dataframe.to_numpy()
            webids = webids[0]
            get_query = {'request' : [] }
            tag_inputs = {}

            # Create the post request for batch url
            for idx in range(0,len(webids)):
                tag_inputs[str(columnnamelist[idx])] = {"Method": "GET","Resource": self.get_request_url.format(webids[idx]),"Headers": {"Cache-Control": "no-cache"}}
            
            # import pdb; pdb.set_trace()
            # post the request for values
            if config.SERVER=="DEVELOPMENT":
                response = requests.post(url,json=tag_inputs, auth=(self.username, self.password), verify=False)
            else:
                headers = {'cache-control': "no-cache",}
                # result = requests.get(url, headers=headers, timeout=5, verify=False)
                # print(tag_inputs)
                # import pdb; pdb.set_trace()
                response = requests.post(url,json=tag_inputs,headers=headers, timeout=5, verify=False)

            content = response.json()
            # Two dictionaries are created as it will be converted into dataframe and will be used in vbm adaptor
            # Values will be used for prediction purpose
            # Timestamp for updating the prediction results in output tags
            input_value_dataframe = pd.DataFrame({ key: content[key]['Content']['Value'] for key in response.json().keys() }, index=[0])
            input_timestamp_dataframe = pd.DataFrame( { key: content[key]['Content']['Timestamp'] for key in response.json().keys() }, index=[0])  

            # Sort dataframe columnnames
            input_value_dataframe = input_value_dataframe.reindex(sorted(input_value_dataframe.columns), axis=1)
            input_timestamp_dataframe = input_timestamp_dataframe.reindex(sorted(input_timestamp_dataframe.columns), axis=1)    
            return input_value_dataframe,input_timestamp_dataframe
        
        except Exception as ex:
            # Log error 
            config.error_logger(ex,cur_file_name)



    # Update the ouptput to the server
    def update_output_data(self, output_dataframe,timestamp_datframe):
        """
            Get stream set url, read output tag web id from csv file.
            Create body for put request and post it to the server.
        """
        
        try:
    
            # request url 
            url = self.streamset_url
            # Get input values's timestamp
            timestamps = timestamp_datframe.to_numpy()
            timestamps = timestamps[0]
            # Collect prediction results
            output_dataframe = output_dataframe.reindex(sorted(output_dataframe.columns), axis=1)
            predictions = output_dataframe.to_numpy()
            predictions = predictions[0]
            # Get output tag's web id
            input_dataframe = pd.read_csv(self.output_tag_path)
            columnnamelist = input_dataframe.columns.tolist()
            webids = input_dataframe.to_numpy()
            webids = webids[0]        
            # Generate request body
            tag_ouputs = []
            for idx in range(0,len(webids)):
                tag_ouputs.append({"WebId": webids[idx],"Items": [{"Timestamp": timestamps[idx],"UnitsAbbreviation": "","Good": True,"Questionable": False,"Value": predictions[idx]}]})
            #post the request
            if config.SERVER=="DEVELOPMENT":
                
                response = requests.post(url,json=tag_ouputs, auth=(self.username, self.password), verify=False)
            else:
                headers = {'cache-control': "no-cache",}

                response = requests.post(url,json=tag_ouputs,headers=headers, timeout=5, verify=False)
            return response.status_code

        except Exception as ex:
            # Log error 
            config.error_logger(ex,cur_file_name)



    # Extract tags and web ID from json file
    def read_tag_webid_from_json(self):
        """
            Read json file with tag name, webid
            Create a csv file with tag name and its corresponding webid
        """

        try:

            # Loading the json file
            model_input_dictionary = {}

            jsonfile = open(config.JSON_FILE_PATH)

            response_points = json.load(jsonfile)

            for point in response_points['Items']:
                # assign webid to each tag name 
                model_input_dictionary[point['Name']] = point['WebId']

            tags = pd.DataFrame(model_input_dictionary,  index=[0])

            tags = tags.reindex(sorted(tags.columns), axis=1)

            tags.to_csv(config.IN_TAG_WEBID)

            return 200

        except Exception as ex:
            # Log error 
            config.error_logger(ex,cur_file_name)

        


# connectionObj = ConnectionPI()
# response_status = connectionObj.read_tag_webid_from_json()
# print(response_status)