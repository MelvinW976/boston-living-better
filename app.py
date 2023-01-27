from flask import Flask, jsonify, request, render_template
from dateutil.relativedelta import relativedelta
from flask_caching import Cache
from flask import render_template
from azure.cosmos import CosmosClient
from config import CLOUD_CONFIGURE
import json
from dateutil import parser
import numpy as np
import pandas as pd
from database import convert_to_cosmos_time, data_between, category_data_between
from data_process import get_time_cache, cache_from_database, get_cache
import plotly.graph_objects as go
from plotly.subplots import make_subplots



app = Flask(__name__)
app.config["DEBUG"] = True
app.config["APPLICATION_ROOT"] = "/"
app.config['TEMPLATES_AUTO_RELOAD'] = True
# current_date = date.today().strftime("%Y-%m-%d")
# 2017,1,1,15,0,0

endpoint = CLOUD_CONFIGURE['END_POINT']
key = CLOUD_CONFIGURE['KEY']
client = CosmosClient(endpoint, key)

database_name = 'blb'
database = client.get_database_client(database_name)
container = database.get_container_client(container='test_for_marker')



cache = Cache(app)
# @app.route('/get_suggestions', methods=["GET", "POST"])
# def retrive_data():
#     # handle the input of the user and retrieve the data (List[List]) from the database
#     return
 # handle the input of the user and retrieve the data (List[List]) from the database
# def generate_markers():
#     # generate the markers according to the lon lat (retrieved list) for the map
#     return
@app.route("/get_suggestions")

def read_area():
    # read the area from the local json file
    with open('./area.json') as f:  
        data = json.load(f)
    return data

def fetch_from_database(concern1,concern2, start_date, end_date):
    # fetch concern_list1 and concern_list2 from the database
    query1= category_data_between(start_date, end_date, concern1)
    query2= category_data_between(start_date, end_date, concern2)
    return query1, query2


def get_zip_count(most_concern_list, second_concern_list):
    # provide the suggestions for the user
    area_list = read_area()['zipcode']

    zipcode_map={}
    for area in area_list:
        zip_info=[]
        zip_info.append(area['lon'])
        zip_info.append(area['lat'])
        zip_info.append(area['radius'])
        if zipcode_map.get(area['zip']) is None:
            zipcode_map[area['zip']] = zip_info
    zip_count={} # key: zip, value: List[List[int]] (most_concern, second_concern, infrastructure)
    #Count # of most concern and second concern in the period for each area
    for item in most_concern_list:
        #print(item)  
        zipcode = item['val'][4]
        tmp= [0, 0]
        zip_count[zipcode]= zip_count.get(zipcode, tmp)
        zip_count[zipcode][0]+=1
    for item in second_concern_list: 
        zipcode = item['val'][4]
        tmp= [0, 0]
        zip_count[zipcode]= zip_count.get(zipcode, tmp)
        zip_count[zipcode][1]+=1
    return zip_count

def get_suggestion(zip_count):
    #print(zip_count)
    zip_list= list(zip_count.keys())
    total_infra= []
    mconcern= []
    sconcern= []
    with open('./sample.json') as f:  
        data = json.load(f)
    # normalize the total number of infrastructure for each area
    for zip in zip_list:
        zip_count[zip].append(data[zip][0])
        zip_count[zip].append(data[zip][1])
        zip_count[zip].append(data[zip][2])
        zip_count[zip].append(data[zip][3])
        total_infra.append(data[zip][4])
        mconcern.append(zip_count[zip][0])
        sconcern.append(zip_count[zip][1])
    total_infra= np.array(total_infra)
    sum= np.sum(total_infra)
    total_infra=[total_infra[i]/sum for i in range(len(total_infra))]
    # normalize the number of most concern and second concern for each area
    mconcern= np.array(mconcern)
    sconcern= np.array(sconcern)
    sum= np.sum(mconcern)
    sum= np.sum(sconcern)
    mconcern=[mconcern[i]/sum for i in range(len(mconcern))] if sum!=0 else [0 for i in range(len(mconcern))]
    sconcern=[sconcern[i]/sum for i in range(len(sconcern))] if sum!=0 else [0 for i in range(len(sconcern))]
    for zip in zip_list:
        zip_count[zip].append(total_infra[zip_list.index(zip)]) 
        zip_count[zip].append(mconcern[zip_list.index(zip)]) 
        zip_count[zip].append(sconcern[zip_list.index(zip)])
    #zip_count [concern1, concern2, infra1, infra2, infra3, infra4, normalized infra, normalized concern1, normalized concern2]
    # sort the zip_count by the normalized number of infrastructure and normalized hate_factor(# of most concern * 0.7 + second concern * 0.3. and return the top 3)
    zip_count = sorted(zip_count.items(), key=lambda x: x[1][6]*0.2-x[1][7]*0.5-x[1][8]*0.3, reverse=True)
    print(zip_count)
    recommendation = []
    l= len(zip_count) if len(zip_count)<3 else 3
    #print(zip_count)
    for i in range(l):
        recommendation.append(zip_count[i])  
    return recommendation
   
@app.route("/listcategory")
def list_category():
    df_cat= pd.read_csv('cat.csv')
    return df_cat['Category'].tolist()

@app.route('/', methods=["GET", "POST"])
def index():
    category_list= list_category()
    return render_template('index.html',  category_list=category_list)

@app.route('/callback/<endpoint>')
def suggestion(endpoint):
    concern1= request.args.get('concern1')
    concern2= request.args.get('concern2')
    period= request.args.get('period')
    time= request.args.get('number')
    end_date= get_time_cache()
    end_date= parser.parse(end_date)
    #print(end_date)

    start_date= end_date
    # print(end_date)
    if period == 'month':
        start_date= (end_date + relativedelta(months=-int(time)))
    elif period == 'day':
        start_date= (end_date + relativedelta(days=-int(time)))
    elif period == 'hour':
        start_date= (end_date + relativedelta(hours=-int(time)))
    # if period == 'hour':
    #     concern1_list, concern2_list= get_cache()
    print(start_date, end_date)
    query1, query2= fetch_from_database(concern1, concern2, start_date, end_date)
    #print(container.query_items(query=query1,enable_cross_partition_query=True))
    concern1_list= list(container.query_items(query=query1,enable_cross_partition_query=True))
    concern2_list= list(container.query_items(query=query2,enable_cross_partition_query=True))
    print(concern1_list)
    print(concern2_list)

    zip_count= get_zip_count(concern1_list, concern2_list)
    
    recommendation= get_suggestion(zip_count)
    if len(recommendation) < 3:
        recommendation= {"1":"n"}
    else: 
        recommendation= {"first": recommendation[0], "second": recommendation[1], "third": recommendation[2]}
    if endpoint == "suggestion":
        return recommendation
    elif endpoint == "get_markers":
        m_list= {"concern1": concern1_list, "concern2": concern2_list}
        return m_list
    else:
        return "Bad endpoint", 400

if __name__ == '__main__':
    app.run(debug=True)