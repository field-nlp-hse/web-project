import os
import subprocess
from shlex import quote
import json
from datetime import datetime
# сериализовать выход парсера

from flask import (
    Flask,
    render_template,
    request,
    # эскейпим пользовательский ввод перед рендером через jinja
    # (чтобы ублажить сергея)
    escape,
    # Response для отправки файлов
    Response,
    # если пользователь не ввел нужный параметр,
    # делаем аборт
    abort
)
from werkzeug.utils import secure_filename
from dicttoxml import dicttoxml
from utils import (
    parse_hfst, 
    TRANSDUCER_MAPPING, 
    is_allowed_extension,
    logger
)

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/asr")
def asr():
    return render_template("asr.html", title="FieldNLP ASR")


@app.route("/parsers", methods=["GET", "POST"])
def parsers():
    params = {
        "title": "FieldNLP Parsers",
        "request_text": "",
        "response_text": [],
        "mapping": TRANSDUCER_MAPPING,
        "curlang": "none"
    }
    if request.method == "GET":
        return render_template(
            "parsers.html",
            **params
        )
    request_text = request.form.get("text", "")
    logger.debug("before file lookup")
    if request.files:
        logger.debug("files found")
        file_ = request.files['file']
        if not is_allowed_extension(file_.filename):
            abort(400)
        request_text = file_.read().decode("utf-8")
        logger.debug(f"Obtained text: {str(request_text)}")
    output_type = request.form.get("output_type", "plaintext")
    
    target_transducer = request.form.get("transducer")
    if not request_text or not target_transducer:
        abort(400)
    # quote to prevent shell insertions
    request_text = quote(request_text)
    # pick a transducer name from list
    target_transducer_file = TRANSDUCER_MAPPING[target_transducer]["filename"]
    echo_process = subprocess.Popen(
        ["echo", request_text],
        stdout=subprocess.PIPE
    )
    ana_process = subprocess.run(
        ["hfst-proc", target_transducer_file],
        stdin=echo_process.stdout,
        capture_output=True
    )
    returncode = ana_process.returncode
    response_text = ana_process.stdout
    # reject request on error
    if returncode != 0 or not response_text:
        abort(400)
    # decode output from bytes
    response_text = response_text.decode("utf-8")
    response_list = parse_hfst(response_text)
    if output_type == "json":
        json_text = json.dumps(response_list, ensure_ascii=False)
        response = Response(json_text, mimetype="application/json")
        response.headers['Content-Disposition'] = (
            'attachment; filename="{}.json"'.format(datetime.now())
        )
        return response
    elif output_type == "xml":
        xml_text = str(dicttoxml(
            response_list, custom_root="analyses", attr_type=False
        ).decode('utf-8'))
        response = Response(xml_text, mimetype="application/xml")
        response.headers['Content-Disposition'] = (
            'attachment; filename="{}.xml"'.format(datetime.now())
        )
        return response
    # if no files have been requested, return a template
    params.update({
        "request_text": escape(request_text),
        "response_text": response_list,
        "curlang": target_transducer
    })
    return render_template(
        "parsers.html",
        **params            
    )


@app.route("/dictionaries")
def dictionaries():
    return render_template("dictionaries.html", title="FieldNLP Dictionaries")


@app.errorhandler(400)
def handle_400(error):
    return render_template("400.html", error=error), 400


@app.errorhandler(404)
def handle_404(error):
    return render_template("404.html", error=error), 404


@app.errorhandler(403)
def handle_403(error):
    return render_template("400.html", error=error), 403


@app.errorhandler(500)
def handle_500(error):
    return render_template("500.html", error=error), 500


if __name__ == "__main__":
    app.config["SECRET_KEY"] = "xfnjMCLYhzFUi$4IoQDRe~sSEoe|OprmKGPW68lOgph#Cgty"
    app.run(host="0.0.0.0", debug=True)
