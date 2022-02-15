# CARBON ANODE DENSITY PREDICTION

######################################################

#  Project Name: Sugar PH Forcasting
#  File : config.py
#       Contains configuration for the script
#  Version: 1.1.0

######################################################

import logging



SERVER = "PRODUCTION"
MODEL = "PH-PEDICTOR"

if SERVER == "PRODUCTION":
# '''access_token = "oRswGaADCgEAoxIEEAEAAABDh+CIwTbjqQAAAAA="

# result = requests.get("https://localhost/piwebapi",headers={'Content-Type':'application/json','Authorization': 'Bearer {}'.format(access_token)})'''

    URL = 'https://localhost/piwebapi'
    USERNAME = 'Admin'
    PASSWORD = 'Admin'
    BATCH_URL = "https://localhost/piwebapi/batch"
    STREAMSET_URL = "https://localhost/piwebapi/streamsets/recorded"
    GET_REQUEST_URL = "https://localhost/piwebapi/streams/{0}/value"
    STATEMATRIX_PATH = "PH\\Data\\9.1\\Th_infer.csv"
    MODEL_PATH='PH\\model\\9.1\\DCM_model.pkl'
    JSON_FILE_PATH = "PH\\cal_tag_prod.json"
    LOGGER_PATH = "PH\\LOGS\\logs_prod.log"
    PREDICT_PATH = 'PH\\CSV\\TEST_FILE.csv'
    PREDICTED_FILE = 'dataset\\prediction.csv'
    SCALAR_PATH = 'model\\scalar.pkl'
    # MODEL_ROOT = ROOT_URL
    DATA_PATH = 'PH\\Data\\Interpolate_oneday_data.csv'
    IN_TAG_WEBID = "PH\\CSV\\INPUT_TAG_WEBID_PROD.csv"
    OUT_TAG_WEBID ="PH\\CSV\\OUTPUT_TAG_WEBID_PROD.csv"
    # IN_TAG_WEBID = "PH\\CSV\\INPUT_TAG_WEDID_LOCAL.csv"
    # OUT_TAG_WEBID ="PH\\CSV\\OUTPUT_TAG_WEDID_LOCAL.csv"
    # JSON_FILE_PATH = ROOT+"cal_tag_prod.json"
    # LOGGER_PATH = ROOT+"LOGS\\logs_production.log"

if SERVER == "DEVELOPMENT":

    URL = 'https://207.246.95.193/piwebapi'
    USERNAME = 'Administrator'
    PASSWORD = 'B2j[H94BsLdr%5wp'
    BATCH_URL = "https://207.246.95.193/piwebapi/batch"
    STREAMSET_URL = "https://207.246.95.193/piwebapi/streamsets/recorded"
    GET_REQUEST_URL = "https://207.246.95.193/piwebapi/streams/{0}/value"
    STATEMATRIX_PATH = "PH\\Data\\9.1\\Th_infer.csv"
    MODEL_PATH='PH\\model\\9.1\\DCM_model.pkl'
    JSON_FILE_PATH = "PH\\cal_tag_prod.json"
    LOGGER_PATH = "PH\\LOGS\\logs_prod.log"
    PREDICT_PATH = 'PH\\CSV\\TEST_FILE.csv'
    PREDICTED_FILE = 'dataset\\prediction.csv'
    SCALAR_PATH = 'model\\scalar.pkl'
    # MODEL_ROOT = ROOT_URL
    DATA_PATH = 'PH\\Data\\Interpolate_oneday_data.csv'
    # IN_TAG_WEBID = "PH\\CSV\\INPUT_TAG_WEBID_PROD.csv"
    # OUT_TAG_WEBID ="PH\\CSV\\OUTPUT_TAG_WEBID_PROD.csv"
    IN_TAG_WEBID = "PH\\CSV\\INPUT_TAG_WEDID_LOCAL.csv"
    OUT_TAG_WEBID ="PH\\CSV\\OUTPUT_TAG_WEDID_LOCAL.csv"
    # JSON_FILE_PATH = ROOT+"cal_tag_prod.json"
    # LOGGER_PATH = ROOT+"LOGS\\logs_production.log"
# Logger Initialization
logging.getLogger(__name__)
logging.basicConfig(filename=LOGGER_PATH,level=logging.DEBUG , filemode='a', format='%(name)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)


# Error handler
def error_logger(ex,cur_file_name):
    """
        Logs the exception error in to the log file
    """
    msg_code = type(ex).__name__
    exmsg = ex.args        
    error_message = str(cur_file_name) +str(' | ')+ str(msg_code) +str(' | ')+ str(exmsg)
    logging.error(str(error_message))
