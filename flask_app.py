import os

from flask import Flask
from flask import render_template

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return render_template('home.html', title = 'Home Page')

if __name__ == '__main__':
    app.config["SECRET_KEY"] = 'xfnjMCLYhzFUi$4IoQDRe~sSEoe|OprmKGPW68lOgph#Cgty'
    app.run(host='0.0.0.0', debug = True)