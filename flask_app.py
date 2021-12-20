import os
import subprocess
from shlex import quote
import json
# сериализовать выход парсера
import re

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


def parse_hfst(hfst_out: str) -> list:
    """turn hfst output into serializeable format"""
    words = re.findall(r"(?<=\^).+?(?=\$)", hfst_out)
    out_dicts = []
    for word in words:
        parts = word.split("/")
        word_dict = {"token": parts[0], "analyses": []}
        # if word is unrecognized, use placeholder
        if parts[1].startswith("*"):
            word_dict["analyses"].append(
                {
                    "lemma": "UNK",
                    "gloss": "UNK"
                }
            )
            out_dicts.append(word_dict)
            continue
        for part in parts[1:]:
            if part.startswith("<"):
                word_dict["analyses"].append(
                    {
                        "lemma": "" if not (x := re.search("(?<=\>)\w+(?=\<)", part)) else x.group(),
                        "gloss": ".".join(
                            re.findall(r"[^<>]+", part)
                        )
                    }
                )
            else:
                breakpnt = part.find("<")
                word_dict["analyses"].append(
                    {
                        "lemma": part[:breakpnt],
                        # change gloss format
                        "gloss": ".".join(
                            re.findall(r"[^<>]+", part[breakpnt:])
                        )
                    }
                )
        out_dicts.append(word_dict)
    return out_dicts

@app.route("/parsers", methods=["GET", "POST"])
def parsers():
    TRANSDUCER_MAPPING = {
        "abz": {
            "html_name": "Абазинский",
            "filename": "abaza.ana.hfstol",
        },
        "bgv-cyr": {
            "html_name": "Багвалинский (аварский алфавит)",
            "filename": "merged.hfstol",
        },
        "bgv-lat": {
            "html_name": "Багвалинский (транскрипция)",
            "filename": "merged.tr.hfstol"
        }
    }
    params = {
        "title": "FieldNLP Parsers",
        "request_text": "",
        "response_text": [],
        "mapping":TRANSDUCER_MAPPING,
        "curlang": "none"
    }
    if request.method == "GET":
        return render_template(
            "parsers.html",
            **params
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
    # quote to prevent shell insertions
    request_text = quote(request_text)
    # pick a transducer name from list
    target_transducer_file = TRANSDUCER_MAPPING[target_transducer]["filename"]
    echo_process = subprocess.Popen(
        ["echo", request_text],
        stdout=subprocess.PIPE
    )
    ana_process = subprocess.run(
        ["hfst-proc", target_transducer_file, request_text],
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
    response_list = parse_hfst(response_text)
    if output_type == "json":
        json_text = json.dumps(response_list)
        return Response(json_text, mimetype="application/json")
    elif output_type == "xml":
        xml_text = str(dicttoxml(
            response_list, custom_root="analyses", attr_type=False
        ))
        return Response(xml_text, mimetype="application/xml")
    # if no files have been requested, return a template
    params.update({
        "input_text": request_text,
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


if __name__ == "__main__":
    app.config["SECRET_KEY"] = "xfnjMCLYhzFUi$4IoQDRe~sSEoe|OprmKGPW68lOgph#Cgty"
    app.run(host="0.0.0.0", debug=True)
