# process the data retrieved, 
from config import CLOUD_CONFIGURE, REDIS_CONFIGURE
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azureml.opendatasets import BostonSafety
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import uuid
from uszipcode import SearchEngine
import redis
from database import data_between
import json
"""
Initialize Cosmos DB
"""
endpoint = CLOUD_CONFIGURE['END_POINT']
key = CLOUD_CONFIGURE['KEY']
client = CosmosClient(endpoint, key)
database_name = 'blb'
database = client.create_database_if_not_exists(id=database_name)
container = database.create_container_if_not_exists(
    id='test_for_marker', 
    partition_key=PartitionKey(path="/id"),
)
search = SearchEngine()
myHostname = REDIS_CONFIGURE['myHostname']
myPassword = REDIS_CONFIGURE['myPassword']
r = redis.StrictRedis(host=myHostname, port=6380,
                      password=myPassword, ssl=True)
    

def get_zipcode(lon, lat):
    return search.by_coordinates(lat, lon, returns=1)[0].to_dict()["zipcode"]

def data_preprocess(df):
    df.dateTime=df.dateTime.dt.strftime('%Y-%m-%d %X').replace(' ','T',regex=True)
    df['id'] = [uuid.uuid4() for _ in range(len(df.index))]
    df['id'] = df['id'].astype(str)
    df['zipcode']=df.apply(lambda x: get_zipcode(x.longitude, x.latitude), axis=1)
    return df

def upload_data(df):
    for row in df.iterrows():
        row = row[1]
        key_str = str(row['id'])
        val_ = [row['dateTime'],row['latitude'], row['longitude'], row['category'], row['zipcode']]
        container.upsert_item(dict(id = key_str, val = val_))
 
def fetch_from_azureml(current_time):
    end_date = current_time
    start_date = end_date + relativedelta(hours=-12)
    safety = BostonSafety(start_date=start_date, end_date=end_date)
    safety = safety.to_pandas_dataframe()
    return safety

def set_cache(list_json):
    r.set('data', list_json)

def set_time_cache(time):
    r.set('time', time)

def get_cache():
    return r.get('data')
def get_time_cache():
    return r.get('time')

def cache_from_database(current_time):
    end_date= current_time
    start_date = end_date + relativedelta(hours=-12)
    query = data_between(start_date, end_date)
    data= list(container.query_items(query=query,enable_cross_partition_query=True))
    data_json=json.dumps(data)
    set_cache(data)

def test_upload(val_):
    container.upsert_item(dict(id = uuid.uuid4().hex, val = val_))

if __name__ == '__main__':
    print("FETCHING DATA FROM YAHOO")