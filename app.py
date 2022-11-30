from flask import Flask, request, render_template,request,redirect,url_for
from flask_caching import Cache
from flask import render_template
from azure.cosmos import CosmosClient
from config import CLOUD_CONFIGURE
import geopy
import json
import os
import collections
import overpy
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["APPLICATION_ROOT"] = "/"
app.config['TEMPLATES_AUTO_RELOAD'] = True
# current_date = date.today().strftime("%Y-%m-%d")
current_date = "2017-01"
endpoint = CLOUD_CONFIGURE['END_POINT']
key = CLOUD_CONFIGURE['KEY']
client = CosmosClient(endpoint, key)

database_name = 'blb'
database = client.get_database_client(database_name)
container = database.get_container_client(container='blb_container')

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
def get_zipcode(lon, lat):
    # get the zipcode, name, center location and radius of the input location by geopy
    geolocator = geopy.geocoders.Nominatim(user_agent="my-application")
    location = geolocator.reverse("{}, {}".format(lat, lon))
    address = location.raw['address']
    zipcode = address.get('postcode', '')
    return zipcode

    

def get_shops(latitude, longitude):
    # Initialize the API
    api = overpy.Overpass()
    # Define the query
    query = """(node["shop"](around:500,{lat},{lon});
                node["building"="retail"](around:500,{lat},{lon});
                node["building"="supermarket"](around:500,{lat},{lon});
                node["healthcare"="pharmacy"](around:500,{lat},{lon});
            );out;
            """.format(lat=latitude, lon=longitude)
    # Call the API
    result = api.query(query)
    return result
def get_suggestions(most_concern, second_concern, period):
    item_list=[]
    cur_year= current_date[:4]
    start_year = int(cur_year)-int(period) 
    start_date = str(start_year) + current_date[4:]
    query = "SELECT * FROM c WHERE c.id BETWEEN '{}%' and '{}%'".format(start_date, current_date)
    for item in list(container.query_items(
                                query=query,
                                enable_cross_partition_query=True)):
        item_list.append(item)
    counter= collections.Counter(item['val'][2])
    most_concern = counter.most_common(1)[0][0]
    second_concern = counter.most_common(2)[1][0] 
    most_concern_marker=''
    second_concern_marker=''
    idd= 0
    # generate the markers for most concern and second concern
    most_concern_list = []
    second_concern_list = []
    for item in item_list:
        if item['val'][2] == most_concern:
            most_concern_list.append(item)
            idd+=1
            lon = item['val'][0]
            lat = item['val'][1]
            cat = item['val'][2]
            most_concern_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
                {idd}.addTo(map).bindPopup('{cat}');".format(idd="idd"+str(idd), latitude=lat,\
                                                                            longitude=lon, cat=cat)
        elif item['val'][2] == second_concern:
            second_concern_list.append(item)
            idd+=1
            lon = item['val'][0]
            lat = item['val'][1]
            cat = item['val'][2]
            second_concern_marker += "var {idd} = L.marker([{latitude}, {longitude}]);\
                {idd}.addTo(map).bindPopup('{cat}');".format(idd="idd"+str(idd), latitude=lat,\
                                                                            longitude=lon, cat=cat)
    area_list = []
    #Count # of most concern and second concern in the period for each area
    for item in most_concern_list:
        lon = item['val'][0]
        lat = item['val'][1]    


    # ranking the areas with defined hate_factor:For each area,  Number of most concern * 0.7 + second concern * 0.3. 

@app.route('/', methods=["GET", "POST"])
@cache.cached(timeout=50)
def index():
    markers= ''
    query= "SELECT * FROM c where c.id like '{}%'".format(current_date)
    idd= 0
    for item in list(container.query_items(query=query,enable_cross_partition_query=True)):
        idd+=1
        lat= item['val'][0]
        lon= item['val'][1]
        cat= item['val'][2]
        markers += "var {idd} = L.marker([{latitude}, {longitude}]);\
                {idd}.addTo(map).bindPopup('{cat}');".format(idd="idd"+str(idd), latitude=lat,\
                                                                            longitude=lon, cat=cat)
    return render_template('index.html', markers=markers)

    # if request.method == "POST":
    #     hate1= request.form["hate1"]
    #     hate2= request.form["hate2"]
    #     period= request.form["period"]
    #     item_list= retrive_data(hate1, hate2, period)
    #     if len(item_list) == 0:
    #         return render_template("index.html", no_data=True)

if __name__ == '__main__':
    app.run(debug=True)