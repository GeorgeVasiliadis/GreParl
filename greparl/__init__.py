import time
import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from .SearchEngine import SearchEngine

from mock.MockSearchEngine import MockSearchEngine as MSE
from mock.MockSpeech import mock_speech

def abs_path(relative):
    """Takes the relative path and returns its absolute position in filesystem.
    It is considered that ther relative path lies on the root directory of this
    app.
    """
    return os.path.join(os.path.dirname(__file__), relative)

def create_app(mode="deploy"):
    app = Flask(__name__)

    # Configure Flask
    if mode == "deploy":
        app.config.from_pyfile(abs_path("config/deploy.cfg"))
    elif mode == "debug":
        app.config.from_pyfile(abs_path("config/dev.cfg"))

    # engine = SearchEngine()
    engine = MSE() #MOCK

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/search", methods=["POST"])
    def search():
        q_string = request.form.get("qString")
        t1 = time.time()
        speeches = engine.search(q_string)
        t2 = time.time()
        time_str = f"{(t2-t1):.2f}"
        return render_template("results.html", speeches=speeches, count=len(speeches), time=time_str, q_string=q_string)

    @app.route("/speech/<int:speech_id>")
    def speech(speech_id):
        # speech = engine.speeches_file.get_speech(speech_id)
        speech = mock_speech # MOCK
        return render_template("speech.html", speech=speech)

    @app.route("/predict", methods=["POST", "GET"])
    def predict():
        if request.method == "GET":
            return render_template("predictions/predict.html")
        elif request.method == "POST":
            p_string = request.form.get("pString")
            predictions = engine.predict_party(p_string)
            return render_template("predictions/results.html", predictions=predictions, p_string=p_string)

    return app
