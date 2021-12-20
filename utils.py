import re
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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


ALLOWED_EXTENSIONS = {'txt'}


def is_allowed_extension(filename: str):
    return any(
        map(lambda x: filename.endswith("." + x), ALLOWED_EXTENSIONS) 
    )