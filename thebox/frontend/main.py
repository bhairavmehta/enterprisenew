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

@app.route("/demos/work-play", methods=['GET'])
def work_play():
    return render_template("home.html")


@app.route("/demos/anomaly-detection", methods=['GET'])
def anomaly_detection():
    return render_template("home.html")


@app.route("/demos/peek-over-shoulder", methods=['GET'])
def peek_over_shoulder():
    return render_template("home.html")


@app.route("/demos/let-me-work", methods=['GET'])
def let_me_work():
    return render_template("home.html")


@app.route("/demos/key-strokes", methods=['GET'])
def key_strokes():
    return render_template("keyStrokes.html")


@app.route('/demos/key-strokes', methods=['POST'])
def my_form_post():
    text = request.form['search']
    processed_text = text.lower()
    data = 'me' if np.random.random() < 0.5 else 'notme'

    return render_template("keyStrokes.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)