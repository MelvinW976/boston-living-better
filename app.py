from flask import Flask, request
from flask import render_template
from azure.cosmos import CosmosClient
from config import CLOUD_CONFIGURE
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

@app.route('/', methods=["GET", "POST"])


# @app.route('/get_suggestions', methods=["GET", "POST"])

# def retrive_data():
#     # handle the input of the user and retrieve the data (List[List]) from the database
#     return
 # handle the input of the user and retrieve the data (List[List]) from the database

# def generate_markers():
#     # generate the markers according to the lon lat (retrieved list) for the map
#     return

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