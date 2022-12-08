from flask import Flask, jsonify, request
from config import CLOUD_CONFIGURE
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.core.exceptions import ResourceExistsError
from apscheduler.schedulers.background import BackgroundScheduler
from azureml.opendatasets import BostonSafety
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

from multiprocessing import Pool

import datetime
import logging

import azure.functions as func

app = Flask(__name__)

"""
Initialize Cosmos DB
"""
endpoint = CLOUD_CONFIGURE['END_POINT']
key = CLOUD_CONFIGURE['KEY']
client = CosmosClient(endpoint, key)
database_name = 'blb'
database = client.create_database_if_not_exists(id=database_name)
container = database.create_container_if_not_exists(
    id='container_test', 
    partition_key=PartitionKey(path="/id"),
)

def data_preprocess(df):
    df.dateTime=df.dateTime.dt.strftime('%Y-%m-%d %X').replace(' ','T',regex=True)

def upload_data(df):
    for row in df.iterrows():
        row = row[1]
        key_str = str(row['id'])
        val_ = [row['dateTime'],row['latitude'], row['longitude'], row['category']]
        container.upsert_item(dict(id = key_str, val = val_))

# update Cosmos DB 
def fetch_from_azureml(currentTime):
    end_date = parser.parse(currentTime)
    start_date = end_date + relativedelta(days=-1)
    safety = BostonSafety(start_date=start_date, end_date=end_date)
    safety = safety.to_pandas_dataframe()
    return safety

# sched = BackgroundScheduler() 
# sched.add_job(fetch_from_azureml, 'interval', minutes=1) # call update function every one minute
# sched.start()
