import os
import re
import json
import requests
from enum import Enum
from dataclasses import is_dataclass, asdict
from urllib import request
from typing import Union
from abc import ABC, abstractmethod


APP_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_PATH = os.path.join(APP_PATH, "assets")
BACKEND_PATH = os.path.join(APP_PATH, "src")
DATA_PATH = os.path.join(APP_PATH, "data")
ASSETS_PATH = os.path.join(FRONTEND_PATH, "assets")
IMAGE_ASSETS_PATH = os.path.join(ASSETS_PATH, "images")
BASE_GENSHIN_CDN_URL = "https://api.genshin.dev"
BASE_GENSHIN_WIKI_URL = "https://genshin-impact.fandom.com/wiki"

DataResponseType = Union[str, dict, None]


class ResponseFormats(Enum):
    JSON = "json"
    XML = "xml"
    TEXT = "txt"


class Elements(Enum):
    ANEMO = "Anemo"
    GEO = "Geo"
    CRYO = "Cryo"
    PYRO = "Pyro"
    HYDRO = "Hydro"
    ELECTRO = "Electro"
    DENDRO = "Dendro"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class FileProvider:
    def save(self, base_path: str, path: str, data=None, response_format=ResponseFormats.JSON.value) -> None:
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        extension = response_format
        file_path = os.path.join(base_path, f"{path}.{extension}")
        with open(file_path, "w", encoding="utf-8") as f:
            if extension == ResponseFormats.JSON.value:
                json.dump(self if not data else data, f, cls=EnhancedJSONEncoder)
            else:
                print("Unsupported file extension")
        return


class APIRequest(ABC):
    @abstractmethod
    def get():
        raise NotImplementedError

    @staticmethod
    def get_response_data(response, response_format: str) -> DataResponseType:
        if response.status_code != 200:
            return  # There was an error in the request
        if response_format == ResponseFormats.TEXT.value:
            return response.text
        if response_format == ResponseFormats.XML.value:
            return response
        return response.json()


class GenshinCDN(APIRequest):
    @staticmethod
    def get(path: str, response_format: str = ResponseFormats.JSON.value, **kwargs) -> DataResponseType:
        url = f"{BASE_GENSHIN_CDN_URL}{path}"
        response = requests.get(url, **kwargs)
        return APIRequest.get_response_data(response, response_format)


class GenshinWiki(APIRequest):
    TABLE_DATA_IDENTIFIER = ("table", {"class": "wikitable"})

    @staticmethod
    def get(path: str, response_format: str = ResponseFormats.JSON.value, **kwargs) -> DataResponseType:
        url = f"{BASE_GENSHIN_WIKI_URL}{path}"
        response = requests.get(url, **kwargs)
        return APIRequest.get_response_data(response, response_format)

    @staticmethod
    def get_released_character_ascension_materials(**kwargs) -> dict:
        character_ascension_materials_page = GenshinWiki.get(
            path="/Character_Ascension_Materials", response_format=ResponseFormats.TEXT.value
        )
        CARD_IMAGE_WHITELIST = ["alt", "data-src", "data-image-key"]

        def get_card_images(col):
            card_images = []
            card_image_containers = col.find_all("div", class_="card_image")
            for card_image_container in card_image_containers:
                card_image = card_image_container.find(
                    "img", {whitelist_attr: True for whitelist_attr in CARD_IMAGE_WHITELIST}
                )
                # Remove any attributes from the card image that are not allowed
                for attr in [attr for attr in card_image.attrs if attr not in CARD_IMAGE_WHITELIST]:
                    del card_image[attr]
                # There's a child a tag that's a part of the card image container which has the title in the last slug
                a_tag = card_image_container.find("a", {"href": True})
                if a_tag:
                    card_image["title"] = a_tag.attrs["href"].lower().split("/")[-1]
                card_images.append(card_image)
            return card_images

        def parse_ascension_gems(cols: list):
            # This is the ascension gems table with 3 columns, we're only interested in column 2 and 3
            element_to_gems = {}
            for i, col in enumerate(cols[1:]):
                if i == 0:
                    element_name = col.find("a", {"title": True}).attrs["title"].upper()
                else:
                    gem_images = get_card_images(col)
                    element_to_gems[element_name] = [
                        image.attrs.get("title") if "title" in image.attrs else image.attrs.get("alt")
                        for image in gem_images
                    ]
            return element_to_gems

        def parse_other_materials(cols: list):
            # This is for other tables with 2 columns, we're only ones with card_image
            materials_to_character = {}
            for i, col in enumerate(cols):
                if i == 0:
                    material_name = col.find("a", {"href": True}).attrs["href"].lower().split("/")[-1]
                else:
                    material_images = get_card_images(col)
                    materials_to_character[material_name] = [
                        image.attrs.get("title") if "title" in image.attrs else image.attrs.get("alt")
                        for image in material_images
                    ]
            return materials_to_character

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(character_ascension_materials_page, "html.parser")
        # There should only be 3 tables: (1) Ascension materials, (2) Normal boss materials, (3) Local specialties
        ascension_gems = {}
        normal_boss_materials = {}
        local_specialties = {}
        for i, table in enumerate(soup.find_all(*GenshinWiki.TABLE_DATA_IDENTIFIER)):
            # Remove all extra tables from the tooltip
            for div in table.find_all("div", {"class": "tooltip-contents"}):
                div.decompose()
            rows = table.find_all("tr")
            # Skip the header rows for each table
            for row in rows[1:]:
                cols = row.find_all("td")
                if i == 0:  # The first table with Ascension Gems
                    ascension_gems.update(parse_ascension_gems(cols))
                elif i == 1:
                    normal_boss_materials.update(parse_other_materials(cols))
                else:
                    local_specialties.update(parse_other_materials(cols))
        if kwargs.get("invert_boss_materials"):
            normal_boss_materials = (normal_boss_materials, invert_dictionary_list(normal_boss_materials))
        if kwargs.get("invert_local_specialties"):
            local_specialties = (local_specialties, invert_dictionary_list(local_specialties))
        return ascension_gems, normal_boss_materials, local_specialties

    @staticmethod
    def get_released_weapon_ascension_materials() -> dict:
        return


def invert_dictionary_list(mapping: dict) -> dict:
    inverted_dictionary_list = {}
    for key, val in mapping.items():
        for new_key in val:
            inverted_dictionary_list[new_key] = key
    return inverted_dictionary_list


def download_asset(url: str, file_path: str, file_name: str, **kwargs) -> DataResponseType:
    if "http" in url:
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        with open(os.path.join(file_path, file_name), "wb") as f:
            request_details = request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, **kwargs)
            f.write(request.urlopen(request_details).read())
    return


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
