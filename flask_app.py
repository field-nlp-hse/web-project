import os
import subprocess
from shlex import quote

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

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS = {'txt'}


def is_allowed_extension(filename: str):
    return any(
        map(lambda x: filename.endswith("." + x), ALLOWED_EXTENSIONS) 
    )


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/asr")
def asr():
    return render_template("asr.html", title="FieldNLP ASR")


TRANSDUCER_MAPPING = {
    "0":"...",
    "1":"merged.hfstol",
    "2":"merged.tr.hfstol"
}


@app.route("/parsers", methods=["GET", "POST"])
def parsers():
    default_params = {
        "request_text": "Введите текст",
        "response_text": ""
    }
    if request.method == "GET":
        return render_template(
            "parsers.html",
            title="FieldNLP Parsers",
            **default_params
        )
    file_ = request.files.get('file')
    request_text = request.form.get("text")
    # assert that text is submitted either as plaintext or as a file 
    if not (bool(file_) != bool(request_text)):
        return "Invalid query: too many parameters", 400
    if file_:
        if not is_allowed_extension(file_.filename):
            return "Invalid query: disallowed file format", 400
        with open(file_, "r", encoding="utf-8") as textfile:
            request_text = textfile.read()
    output_type = request.form.get("output_type", "plaintext")
    
    target_transducer = request.form.get("transducer")
    if not request_text or not target_transducer:
        return "Invalid query: parameters missing", 400
    # quote against shell insertions
    request_text = quote(request_text)
    # pick a transducer name from list
    target_transducer = TRANSDUCER_MAPPING[target_transducer]
    echo_process = subprocess.Popen(
        ["echo", request_text],
        stdout=subprocess.PIPE
    )
    ana_process = subprocess.run(
        ["hfst-proc", target_transducer, request_text]
        stdin=echo_process.stdout,
        capture_output=True
    )
    returncode = ana_process.returncode
    response_text = ana_process.stdout
    # reject request on error
    if returncode != 0 or not response_text:
        return "Invalid query: bad text", 400
    # decode output from bytes
    response_text = response_text.decode("utf-8")
    if output_type == "json":
        json_text = response_text # to_json(response_text)
        return Response(json_text, mimetype="application/json")
    elif output_type == "xml":
        xml_text = response_text # to_xml(response_text)
        return Response(xml_text, mimetype="application/xml")
    # if no files have been requested, return a template
    params = {}
    params["input_text"] = request_text
    params["response_text"] = response_text # to_html(response_text)
    return render_template(
        "parsers.html",
        title="FieldNLP Parsers",
        **params            
    )


@app.route("/dictionaries")
def dictionaries():
    return render_template("dictionaries.html", title="FieldNLP Dictionaries")


if __name__ == "__main__":
    app.config["SECRET_KEY"] = "xfnjMCLYhzFUi$4IoQDRe~sSEoe|OprmKGPW68lOgph#Cgty"
    app.run(host="0.0.0.0", debug=True)
