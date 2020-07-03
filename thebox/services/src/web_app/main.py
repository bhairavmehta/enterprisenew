from flask import Flask, render_template
from flask import request
from web_app.demos.keystrokes import KeyStrokes, TelemetryClient
import argparse

app = Flask(__name__)
images_path = '../static/images'


def parse_args():
    parser = argparse.ArgumentParser(description='Arguments parser.')
    parser.add_argument('--pubsub_endpoint', type=str, default='localhost:10001',
                        help='IP address of the pubsub endpoint.')
    parser.add_argument('--frontend_ip', type=str, default='localhost', help='IP address of the server.')

    return parser.parse_args()


def replace_multiple_char(st, chars_list, new_st):
    for oldChar in chars_list:
        st = st.replace(oldChar, new_st)
    return st


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


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    key_strokes_app.stop()
    exit()


@app.route("/demos/key-strokes", methods=['GET'])
def key_strokes():
    return render_template("keyStrokes.html")


@app.route('/demos/key-strokes', methods=['POST'])
def my_form_post():
    text = request.form['search']
    processed_text = replace_multiple_char(
        text.lower(), ['.', ',', ':', '?'], ' ')
    tel_client.send_telemetry(processed_text)
    key_strokes_app.wait()
    return render_template("keyStrokes.html", data=key_strokes_app.data)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == "__main__":
    args = parse_args()

    in_topic = "in_topic_ks_infer_test"
    out_topic = "out_topic_ks_notif_test"
    tel_client = TelemetryClient(args.pubsub_endpoint, in_topic)

    key_strokes_app = KeyStrokes(args.pubsub_endpoint, out_topic)
    key_strokes_app.run()
    app.run(host=args.frontend_ip)
