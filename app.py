from flask import Flask, request
from flask import render_template
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["APPLICATION_ROOT"] = "/"
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/', methods=["GET", "POST"])

def retrive_data():
    # handle the input of the user and retrieve the data (List[List]) from the database
    return

def generate_markers():
    # generate the markers according to the lon lat (retrieved list) for the map
    return


def main():
    return render_template('index.html')