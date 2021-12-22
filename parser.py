import re
import subprocess

from flask_restful import fields, marshal

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

analysis_fields = {
    "lemma": fields.String,
    "gloss": fields.String
}

token_fields = {
    "token": fields.String,
    "analyses": fields.List(fields.Nested(analysis_fields))
}


def transducer_lookup(target_transducer: str, request_text: str):
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
    return returncode, response_text 


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
                marshal({"lemma": "UNK", "gloss": "UNK"}, analysis_fields)
            )
            out_dicts.append(marshal(word_dict, token_fields))
            continue
        for part in parts[1:]:
            if part.startswith("<"):
                word_dict["analyses"].append(marshal(
                    {
                        "lemma": "" if not (x := re.search("(?<=\>)\w+(?=\<)", part)) else x.group(),
                        "gloss": ".".join(re.findall(r"[^<>]+", part))
                    },
                    analysis_fields
                ))
            else:
                breakpnt = part.find("<")
                word_dict["analyses"].append(marshal(
                    {
                        "lemma": part[:breakpnt],
                        "gloss": ".".join(re.findall(r"[^<>]+", part[breakpnt:]))
                    },
                    analysis_fields
                ))
        out_dicts.append(marshal(word_dict, token_fields))
    return out_dicts