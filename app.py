from flask import Flask, jsonify, request, render_template,request,redirect,url_for
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
    geolocator = geopy.geocoders.Nominatim(user_agent="my-application")
    location = geolocator.reverse("{}, {}".format(lat, lon))
    address = location.raw['address']
    zipcode = address.get('postcode', '')
    return zipcode

def read_area():
    # read the area from the local json file
    with open('./area.json') as f:  
        data = json.load(f)
    return data

def get_infrastructure(latitude, longitude, radius):
    # Initialize the API
    api = overpy.Overpass()
    # Define the query
    shop_query = """(node["shop"](around:{r},{lat},{lon});
                node["building"="retail"](around:{r},{lat},{lon});
                node["building"="supermarket"](around:{r},{lat},{lon});
                node["healthcare"="pharmacy"](around:{r},{lat},{lon});
                node["amenity"="restaurant"](around:{r},{lat},{lon});
                node["amenity"="bank"](around:{r},{lat},{lon});
            );out;
            """.format(r=radius,lat=latitude, lon=longitude)
    restaurants_query = """(node["amenity"="restaurant"](around:{r},{lat},{lon});
                node["amenity"="fast_food"](around:{r},{lat},{lon});
                node["amenity"="cafe"](around:{r},{lat},{lon});
                node["amenity"="bar"](around:{r},{lat},{lon});
                );out;
            """.format(r=radius,lat=latitude, lon=longitude)
    Hotels_query = """(node["tourism"="hotel"](around:{r},{lat},{lon});
                node["tourism"="motel"](around:{r},{lat},{lon});
            );out;
            """.format(r=radius,lat=latitude, lon=longitude)
    Hospitals_query = """(node["amenity"="hospital"](around:{r},{lat},{lon});
            );out;
            """.format(r=radius,lat=latitude, lon=longitude)
    # Call the API
    shops= api.query(shop_query)
    restaurants = api.query(restaurants_query)
    hotels = api.query(Hotels_query)
    hospitals = api.query(Hospitals_query)
    return shops, restaurants, hotels, hospitals

def fetch_data(period):
    item_list=[]
    cur_year= current_date[:4]
    start_year = int(cur_year)-int(period) 
    start_date = str(start_year) + current_date[4:]
    query = "SELECT * FROM c WHERE c.id BETWEEN '{}%' and '{}%'".format(start_date, current_date)
    for item in list(container.query_items(
                                query=query,
                                enable_cross_partition_query=True)):
        item_list.append(item)
    return item_list

def generate_markers(most_concern, second_concern, item_list):
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
    return most_concern_marker, second_concern_marker, most_concern_list, second_concern_list
def get_suggestions(most_concern_list, second_concern_list):
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
        lon = item['val'][0]
        lat = item['val'][1]    
        zipcode = get_zipcode(lon, lat)
        tmp= []([0], [0] ,[0])
        zip_count[zipcode]= zip_count.get(zipcode, tmp)
        zip_count[zipcode][0][0]+=1
    for item in second_concern_list:
        lon = item['val'][0]
        lat = item['val'][1]    
        zipcode = get_zipcode(lon, lat)
        tmp= [](0, 0 ,0)
        zip_count[zipcode]= zip_count.get(zipcode, tmp)
        zip_count[zipcode][1][0]+=1
    zip_list = list(zip_count.keys())
    #Count # of infrastructure in the period for each area
    shop_marker=''
    restaurant_marker=''
    hotel_marker=''
    hospital_marker=''
    for zip in zip_list:
        info= zipcode_map[zip] 
        shops, restaurants, hotels, hospitals = get_infrastructure(info[1], info[0], info[2])
        zip_count[zip][2]= [len(shops.nodes), len(restaurants.nodes), len(hotels.nodes), len(hospitals.nodes), 
            len(shops.nodes)+len(restaurants.nodes)+len(hotels.nodes)+len(hospitals.nodes)]
    
    # sort the zip_count by the number of infrastructure and hate_factor:Num of most concern * 0.7 + second concern * 0.3. and return the top 3
    zip_count = sorted(zip_count.items(), key=lambda x: x[1][2][4]*0.3+x[1][0][0]*0.7+x[1][1][0]*0.3, reverse=True)
    recommendation = []
    for i in range(3):
        recommendation.append(zip_count[i][0])  
    return recommendation
   

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