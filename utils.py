import logging
import sys
import json


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


ALLOWED_EXTENSIONS = {'txt'}


def is_allowed_extension(filename: str):
    return any(
        map(lambda x: filename.endswith("." + x), ALLOWED_EXTENSIONS) 
    )