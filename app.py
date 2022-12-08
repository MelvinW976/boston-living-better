from flask import Flask, jsonify, request, render_template
import datetime
from dateutil.relativedelta import relativedelta
from flask_caching import Cache
from flask import render_template
from azure.cosmos import CosmosClient
from config import CLOUD_CONFIGURE
import json
import plotly
from dateutil import parser
import numpy as np
import pandas as pd
from database import convert_to_cosmos_time, data_between, category_data_between
from data_process import get_cache, set_cache, get_time_cache
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import redis
from TimerTrigger1 import get_current_time



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

# def get_infrastructure(latitude, longitude, radius):
#     # Initialize the API
#     api = overpy.Overpass()
#     # Define the query
#     shop_query = """(node["shop"](around:{r},{lat},{lon});
#                 node["building"="retail"](around:{r},{lat},{lon});
#                 node["building"="supermarket"](around:{r},{lat},{lon});
#                 node["healthcare"="pharmacy"](around:{r},{lat},{lon});
#                 node["amenity"="restaurant"](around:{r},{lat},{lon});
#                 node["amenity"="bank"](around:{r},{lat},{lon});
#             );out;
#             """.format(r=radius,lat=latitude, lon=longitude)
#     restaurants_query = """(node["amenity"="restaurant"](around:{r},{lat},{lon});
#                 node["amenity"="fast_food"](around:{r},{lat},{lon});
#                 node["amenity"="cafe"](around:{r},{lat},{lon});
#                 node["amenity"="bar"](around:{r},{lat},{lon});
#                 );out;
#             """.format(r=radius,lat=latitude, lon=longitude)
#     Hotels_query = """(node["tourism"="hotel"](around:{r},{lat},{lon});
#                 node["tourism"="motel"](around:{r},{lat},{lon});
#             );out;
#             """.format(r=radius,lat=latitude, lon=longitude)
#     Hospitals_query = """(node["amenity"="hospital"](around:{r},{lat},{lon});
#             );out;
#             """.format(r=radius,lat=latitude, lon=longitude)
#     # Call the API
#     shops= api.query(shop_query)
#     restaurants = api.query(restaurants_query)
#     hotels = api.query(Hotels_query)
#     hospitals = api.query(Hospitals_query)
#     return shops, restaurants, hotels, hospitals

def fetch_from_database(concern1,concern2, start_date, end_date):
    # fetch concern_list1 and concern_list2 from the database
    query1= category_data_between(start_date, end_date, concern1)
    query2= category_data_between(start_date, end_date, concern2)
    return query1, query2

# def generate_concern_markers(most_concern_list, second_concern_list):
#     concern_marker=''
#     idd= 0
#     # generate the markers for most concern and second concern
#     for item in most_concern_list:
#         idd+=1
#         lat = item['val'][1]
#         lon = item['val'][2]
#         cat = item['val'][3]
#         time= item['val'][0]
#         concern_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
#             {idd}.addTo(map).bindPopup('{cat}<br>{time}');".format(idd="idd"+str(idd), latitude=lat,\
#                                                                         longitude=lon, cat=cat, time=time)
#     for item in second_concern_list:
#         idd+=1
#         lat = item['val'][1]
#         lon = item['val'][2]
#         cat = item['val'][3]
#         time= item['val'][0]
#         concern_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
#             {idd}.addTo(map).bindPopup('{cat} <br> {time}');".format(idd="idd"+str(idd), latitude=lat,\
#                                                                         longitude=lon, cat=cat, time= time)
#     return concern_marker

# def generate_infra_markers(shops, restaurants, hotels, hospitals):
#     infra_marker= ''
#     idd= 0
#     for shop in shops.nodes:
#         idd+=1
#         lon = shop.lon
#         lat = shop.lat
#         try:
#             shop_brand = shop.tags['brand']
#         except:
#             shop_brand = 'null'
#         infra_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
#             {idd}.addTo(map).bindPopup('shop<br> {brand}');".format(idd="shop"+str(idd), latitude=lat,\
#                                                                         longitude=lon, brand=shop_brand)
#     for restaurant in restaurants.nodes:
#         idd+=1
#         lon = restaurant.lon
#         lat = restaurant.lat
#         try:
#             shop_brand = restaurant.tags['brand']
#         except:
#             shop_brand = 'null'
#         infra_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
#             {idd}.addTo(map).bindPopup('restaurant<br> {brand}');".format(idd="rest"+str(idd), latitude=lat,\
#                                                                         longitude=lon, brand=shop_brand)
#     for hotel in hotels.nodes:
#         idd+=1
#         lon = hotel.lon
#         lat = hotel.lat
#         try:
#             shop_brand = hotel.tags['brand']
#         except:
#             shop_brand = 'null'
#         infra_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
#             {idd}.addTo(map).bindPopup('hotel <br> {brand}');".format(idd="hotel"+str(idd), latitude=lat,\
#                                                                         longitude=lon, brand=shop_brand)
#     for hospital in hospitals.nodes:
#         idd+=1
#         lon = hospital.lon
#         lat = hospital.lat
#         try:
#             shop_brand = hospital.tags['brand']
#         except:
#             shop_brand = 'null'
#         infra_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
#             {idd}.addTo(map).bindPopup('hospital <br> {shop_brand}');".format(idd="hosp"+str(idd), latitude=lat,\
#                                                                         longitude=lon, shop_brand=shop_brand)
#     return infra_marker


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
    # query= "SELECT * FROM c where c.val[0] like '{}%'".format(current_date)
    # idd= 0
    # for item in list(container.query_items(query=query,enable_cross_partition_query=True)):
    #     idd+=1
    #     lat= item['val'][1]
    #     lon= item['val'][2]
    #     cat= item['val'][3]
    #     markers += "var {idd} = L.marker([{latitude}, {longitude}]);\
    #             {idd}.addTo(map).bindPopup('{cat}');".format(idd="idd"+str(idd), latitude=lat,\
    #                                                                         longitude=lon, cat=cat)
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
    query1, query2= fetch_from_database(concern1, concern2, start_date, end_date)
    for item in list(container.query_items(query=query1,enable_cross_partition_query=True)):
        print(item)
    #print(container.query_items(query=query1,enable_cross_partition_query=True))
    concern1_list= list(container.query_items(query=query1,enable_cross_partition_query=True))
    concern2_list= list(container.query_items(query=query2,enable_cross_partition_query=True))
    #print(len(concern1_list), len(concern2_list))
    print(start_date, end_date)
    print(len(concern1_list), len(concern2_list))
    # print("fetching data from database...")
    # print(concern1, concern2, start_date, end_date)
    # print(len(concern1_list), len(concern2_list))
    # print("computing....")
    # cur_time= datetime.datetime.now()
    # end_date= cur_time.strftime("%Y-%m-%d")
    # start_date= cur_time
    # marker= {}
    # if period == 'month':
    #     start_date= (cur_time - datetime.timedelta(days=30*int(time))).strftime("%Y-%m-%d")
    # elif period == 'year':
    #     start_date= (cur_time - datetime.timedelta(days=365*int(time))).strftime("%Y-%m-%d")
    # concern1_list= category_data_between_dates(concern1, start_date, end_date)
    # concern2_list= category_data_between_dates(concern2, start_date, end_date)
    # concern1_list= [{"id": "0",

    zip_count= get_zip_count(concern1_list, concern2_list)
    
    print(zip_count)
    recommendation= get_suggestion(zip_count)
    if len(recommendation) < 3:
        recommendation= {"1":"n"}
    else: 
        recommendation= {"first": recommendation[0], "second": recommendation[1], "third": recommendation[2]}
    if endpoint == "suggestion":
        print("in suggestion")
        return recommendation
    elif endpoint == "get_markers":
        m_list= {"concern1": concern1_list, "concern2": concern2_list}
        return m_list
    # elif endpoint == "plot":
    #     # isMonth= period == 'month'
    #     # num= time
    #     # plot_list1= past_concerns(recommendation.key()[0] , cur_time, isMonth, num) # fetch data constrained by zipcode, concern types
    #     # plot_list2= past_concerns(recommendation.key()[1] , cur_time, isMonth, num)
    #     # plot_list3= past_concerns(recommendation.key()[2] , cur_time, isMonth, num)
    #     plot_list1= [{"date": "01", "count":3} , {"date": "02", "count":4} , {"date": "03", "count":5} , {"date": "04", "count":6} , {"date": "05", "count":7} , {"date": "06", "count":8} , {"date": "07", "count":9} , {"date": "08", "count":10} , {"date": "09", "count":11} , 
    #     {"date": "10", "count":12} , {"date": "11", "count":13} , {"date": "12", "count":14} ]
    #     plot_list2= [{"date": "01", "count":3} , {"date": "02", "count":4} , {"date": "03", "count":5} , {"date": "04", "count":6} , {"date": "05", "count":7} , {"date": "06", "count":8} , {"date": "07", "count":9} , {"date": "08", "count":10} , {"date": "09", "count":11} ,
    #     {"date": "10", "count":12} , {"date": "11", "count":13} , {"date": "12", "count":14} ]
    #     plot_list3= [{"date": "01", "count":3} , {"date": "02", "count":4} , {"date": "03", "count":5} , {"date": "04", "count":6} , {"date": "05", "count":7} , {"date": "06", "count":8} , {"date": "07", "count":9} , {"date": "08", "count":10} , {"date": "09", "count":11} ,
    #     {"date": "10", "count":12} , {"date": "11", "count":13} , {"date": "12", "count":14} ]
    #     plot1_df= pd.DataFrame(plot_list1)
    #     plot2_df= pd.DataFrame(plot_list2)
    #     plot3_df= pd.DataFrame(plot_list3)
    #     fig= make_subplots(rows=1, cols=3)
    #     fig.add_trace(go.Scatter(x=plot1_df['date'], y=plot1_df['count'], name=concern1), row=1, col=1)
    #     fig.add_trace(go.Scatter(x=plot2_df['date'], y=plot2_df['count'], name=concern2), row=2, col=1)
    #     fig.add_trace(go.Scatter(x=plot3_df['date'], y=plot3_df['count'], name=concern2), row=3, col=1)
    #     graphJSON= json.dumps(fig, cls= plotly.utils.PlotlyJSONEncoder)
    #     return graphJSON
    # elif endpoint == "concern_marker":
    #     concern_marker= generate_concern_markers(concern1_list, concern2_list)
    #     marker= {'concern': concern_marker}
    #     return marker
    # elif endpoint == "infra_marker":
    #     infra_marker= ''
    #     zip_list= list(recommendation.keys())
    #     for zip in zip_list:
    #         info= zip_count[zip] 
    #         shops, restaurants, hotels, hospitals = get_infrastructure(info[1], info[0], info[2])
    #         infra_marker += generate_infra_markers(shops, restaurants, hotels, hospitals)
            
    #     marker= {'infra': infra_marker}
    #     return marker
    else:
        return "Bad endpoint", 400

if __name__ == '__main__':
    app.run(debug=True)