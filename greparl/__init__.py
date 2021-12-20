import time
import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from .SearchEngine import SearchEngine

def abs_path(relative):
    """Takes the relative path and returns its absolute position in filesystem.
    It is considered that ther relative path lies on the root directory of this
    app.
    """
    return os.path.join(os.path.dirname(__file__), relative)

def create_app():
    app = Flask(__name__)

    # Configure Flask for development
    # *COMMENT OUT BEFOR DEPLOYMENT*
    app.config.from_pyfile(abs_path("config/dev.cfg"))

    engine = SearchEngine(abs_path("data/index/index"), abs_path("data/speeches.csv"))

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
        speech = engine.speeches_file.get_speech(speech_id)
        return render_template("speech.html", speech=speech)
    return app
