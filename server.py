from flask import Flask, jsonify, request
from config import CLOUD_CONFIGURE
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.core.exceptions import ResourceExistsError

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
    id='blb_container', 
    partition_key=PartitionKey(path="/id"),
)


# Initialize Cosmos DB
# update Cosmos DB 
