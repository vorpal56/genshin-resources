import os
import re
import json
import requests
from enum import Enum
from dataclasses import is_dataclass, asdict
from urllib import request


APP_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_PATH = os.path.join(APP_PATH, "assets")
BACKEND_PATH = os.path.join(APP_PATH, "src")
DATA_PATH = os.path.join(APP_PATH, "data")
ASSETS_PATH = os.path.join(FRONTEND_PATH, "assets")
IMAGE_ASSETS_PATH = os.path.join(ASSETS_PATH, "images")
BASE_GENSHIN_CDN_URL = "https://api.genshin.dev"


class ResponseTypes(Enum):
    JSON = "json"
    XML = "xml"
    TEXT = "text"


class Elements(Enum):
    ANEMO = "Anemo"
    GEO = "Geo"
    CRYO = "Cryo"
    PYRO = "Pyro"
    HYDRO = "Hydro"
    ELECTRO = "Electro"
    DENDRO = "Dendro"

    @classmethod
    def has_value(cls, value: str):
        return value in cls._value2member_map_


class GenshinCDN:
    @staticmethod
    def get(path: str, response_type: str = ResponseTypes.JSON.value, **kwargs) -> dict:
        url = f"{BASE_GENSHIN_CDN_URL}{path}"
        response = requests.get(url, **kwargs)
        if response.status_code != 200:
            return  # There was an error in the request
        if response_type == ResponseTypes.TEXT.value:
            return response.text
        if response_type == ResponseTypes.XML.value:
            return response
        return response.json()


def download_asset(url: str, path: str, **kwargs) -> None:
    if "http" in url:
        with open(path, "wb") as f:
            request_details = request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, **kwargs)
            f.write(request.urlopen(request_details).read())
    return


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


def remove_ascii_chars(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\u300c", "[")
    text = text.replace("\u300d", "]")
    text = text.replace("\u00ba", "°")
    text = text.replace("\u200b", "")  # zero width space
    text = text.replace("\u200e", "")  # left-to-right mark
    text = text.replace("\u2013", ":")  # left-to-right mark
    text = text.replace("\xa0", " ")
    text = text.replace("\uFF06", "&")
    text = text.replace(r"−", "-")
    text = text.replace("\u00e2\u02c6\u2019", "-")
    # text = text.encode("ascii", "ignore")
    # return text.decode()
    return text


def remove_extra_whitespace(text: str) -> str:
    return re.sub(r" +", " ", text)
