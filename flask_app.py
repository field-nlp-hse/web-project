import os

from flask import Flask, render_template

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/asr")
def asr():
    return render_template("asr.html", title="FieldNLP ASR")


@app.route("/parsers")
def parsers():
    return render_template("parsers.html", title="FieldNLP Parsers")


@app.route("/dictionaries")
def dictionaries():
    return render_template("dictionaries.html", title="FieldNLP Dictionaries")


if __name__ == "__main__":
    app.config["SECRET_KEY"] = "xfnjMCLYhzFUi$4IoQDRe~sSEoe|OprmKGPW68lOgph#Cgty"
    app.run(host="0.0.0.0", debug=True)
