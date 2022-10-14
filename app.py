from flask import Flask, request
from flask import render_template
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["APPLICATION_ROOT"] = "/"
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index.html')