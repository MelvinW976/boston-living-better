import datetime
import logging
from multiprocessing import Pool
import numpy as np
import azure.functions as func
from data_process import fetch_from_azureml, upload_data, data_preprocess, get_time_cache, set_time_cache , cache_from_database, get_cache

global current_date
current_date = datetime.datetime(2017,1,1,15,0,0)
Counter= 0

def get_current_time():
    #print(current_date)
    return current_date
def main(mytimer: func.TimerRequest) -> None:
    # increase the current date for 1 hour
    global current_date
    current_date = current_date + datetime.timedelta(hours=12)
    # set the time cache
    #print()
    set_time_cache(str(current_date))
    global Counter
    Counter+=1
    if Counter == 12:
        Counter=0 
        cache_from_database(current_date)
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    processed_data = data_preprocess(fetch_from_azureml(current_date))
    # with Pool(8) as p:
    #     p.map(upload_data, np.array_split(processed_data, 8))
    upload_data(processed_data)
    # test_upload(utc_timestamp)
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
