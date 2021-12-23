import os
import csv
from shlex import quote
import json
from datetime import datetime
from gevent.pywsgi import WSGIServer

from flask import (
    Flask,
    render_template,
    request,
    escape,
    jsonify,
    Response,
    abort
)
from flask_restful import Api, Resource, marshal
from werkzeug.utils import secure_filename
from dicttoxml import dicttoxml

from utils import (
    is_allowed_extension,
    logger,
)
from parser import (
    token_fields,
    transducer_lookup,
    parse_hfst,
    TRANSDUCER_MAPPING
)


app = Flask(__name__)
api = Api(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/asr")
def asr():
    return render_template("asr.html", title="FieldNLP ASR")


class ParserList(Resource):
    def get(self):
        return {"parsers": list(TRANSDUCER_MAPPING.keys())}


class ParsedWord(Resource):
    def get(self, parser: str, word: str):
        if parser not in TRANSDUCER_MAPPING or " " in word:
            return {"message": "Invalid query"}, 400
        returncode, response_text = transducer_lookup(parser, word)
        if returncode != 0 or not response_text:
            return {"message": "Invalid query"}, 400
        response_text = response_text.decode("utf-8")
        if "*" in response_text:
            return {"message": "Word out of dictionary"}, 404
        return marshal(parse_hfst(response_text), token_fields)


api.add_resource(ParserList, "/parseapi/parserlist")
api.add_resource(ParsedWord, "/parseapi/<string:parser>/<string:word>")


@app.route("/parsers", methods=["GET", "POST"])
def parsers():
    params = {
        "title": "FieldNLP Parsers",
        "request_text": "",
        "response_text": [],
        "mapping": TRANSDUCER_MAPPING,
        "curlang": "none",
    }
    # logger.debug(str(len(request.args)))
    is_post = request.method == "POST"
    if not is_post and len(request.args) == 0:
        return render_template("parsers.html", **params)
    request_text = request.values.get("text")
    if request.files:
        file_ = request.files["file"]
        if is_allowed_extension(file_.filename):
            request_text = file_.read().decode("utf-8")
    output_type = request.values.get("output-type", "plaintext")
    target_transducer = request.values.get("transducer")
    if not request_text or not target_transducer:
        abort(400)
    # quote to prevent shell insertions
    request_text = quote(request_text)
    # pick a transducer name from list
    returncode, response_text = transducer_lookup(target_transducer, request_text)
    # reject request on error
    if returncode != 0 or not response_text:
        logger.debug("parsing error")
        abort(400)
    # decode output from bytes
    response_text = response_text.decode("utf-8")
    response_list = parse_hfst(response_text)
    if output_type == "json":
        json_text = json.dumps(response_list, ensure_ascii=False)
        response = Response(json_text, mimetype="application/json")
        if is_post:
            response.headers[
                "Content-Disposition"
            ] = 'attachment; filename="{}.json"'.format(datetime.now())
        return response
    elif output_type == "xml":
        xml_text = str(
            dicttoxml(response_list, custom_root="analyses", attr_type=False).decode(
                "utf-8"
            )
        )
        response = Response(xml_text, mimetype="application/xml")
        if is_post:
            response.headers[
                "Content-Disposition"
            ] = 'attachment; filename="{}.xml"'.format(datetime.now())
        return response
    # if no files have been requested, return a template
    params.update(
        {
            "request_text": escape(request_text),
            "response_text": response_list,
            "curlang": target_transducer,
        }
    )
    if not is_post:
        return Response(response_text, mimetype="text/plain")
    return render_template("parsers.html", **params)


@app.route("/dictionaries")
def dictionaries():
    reader = csv.DictReader(open("./static/data/query-result.csv", encoding="utf-8"))
    some_info = "я текст из фласка"
    other_info = "не ждали?"
    return render_template(
        "dictionaries.html",
        some_info={1: some_info, 2: other_info},
        table=reader,
        title="FieldNLP Dictionaries",
    )


@app.route("/submitted")
def submitted():
    return render_template("submitted.html", title="FieldNLP Feedback")


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
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()
