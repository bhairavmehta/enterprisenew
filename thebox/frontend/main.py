from flask import Flask, render_template, send_from_directory
from flask import request
import os
import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image
app = Flask(__name__)
images_path = '../static/images'


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


# @app.route("/", methods=['POST', 'GET'])
# def myfunc():
#
#     new_graph_name = "graph" + str(time.time()) + ".png"
#
#     me = send_from_directory(os.path.abspath(images_path),
#                              'me.png')
#     not_me = send_from_directory(os.path.abspath(images_path),
#                                  'notme.png')
#
#     return render_template("home.html", graph=new_graph_name)


if __name__ == "__main__":
    app.run(debug=True)