import random
import time
import os
from datetime import datetime

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
        if request.form.get("randomGrep"):
            max_ = engine.get_total_speeches()
            id_ = random.randint(1, max_)
            return redirect(url_for("speech", speech_id=id_))
        else:
            q_string = request.form.get("qString")
            t1 = time.time()
            speeches = engine.search(q_string)
            t2 = time.time()
            time_str = f"{(t2-t1):.2f}"
            return render_template("results.html", speeches=speeches, count=len(speeches), time=time_str, q_string=q_string)

    @app.route("/deep-search", methods=["POST"])
    def deep_search():
        q_string = request.form.get("qString")
        t1 = time.time()
        speeches = engine.search_lsa(q_string)
        t2 = time.time()
        time_str = f"{(t2-t1):.2f}"
        return render_template("results.html", speeches=speeches, count=len(speeches), time=time_str, q_string=q_string, deep_search=True)


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

    @app.route("/highlights/<step>", methods=["GET","POST"])
    def highlights(step):
        if not step or step == "attribute":
            attributes = engine.get_available_attributes()
            attributes.add("speech") # I hate myself for doing this :(
            return render_template("highlights/attribute.html", attributes=attributes)
        elif request.method == "POST" and step == "values":
            attribute = request.form.get("attribute")
            if attribute != "speech":
                values = engine.get_attribute_values(attribute)
            else:
                values = None
            if "default_id" in request.form:
                default_id = request.form.get("default_id")
            else:
                default_id = 1
            return render_template("highlights/values.html", attribute=attribute, values=values, default_id=default_id)
        elif request.method == "POST" and step == "results":
            attribute = request.form.get("attribute")
            value = request.form.get("value")
            if attribute != "speech":
                d_start = request.form.get("start")
                d_start = datetime.strptime(d_start, "%Y-%m-%d").date()
                d_end = request.form.get("end")
                d_end = datetime.strptime(d_end, "%Y-%m-%d").date()
            else:
                d_start = None
                d_end = None
            k_results = int(request.form.get("k-results"))
            highlights = engine.get_keywords(attribute, value, d_start, d_end, k=k_results)
            return render_template("highlights/results.html", highlights=highlights, attribute=attribute, value=value, d_start=d_start, d_end=d_end)
    return app
