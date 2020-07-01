from flask import Flask, render_template, send_from_directory
from flask import request
import os
import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image
app = Flask(__name__)
images_path = '../static/images'


@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['search']
    processed_text = text.lower()
    data = 'me' if np.random.random() < 0.5 else 'notme'

    return render_template("home.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)