import json
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple
from src.common.util import EnhancedJSONEncoder, GenshinCDN, BACKEND_PATH

CHARACTER_DATA_PATH = os.path.join(BACKEND_PATH, "characters", "data")


@dataclass
class Character:
    apiname: str
    name: str
    vision: str
    weapon: str
    rarity: int
    constellation: str
    description: str
    skillTalents: List[Dict[str, str]]
    passiveTalents: List[Dict[str, str]]
    constellations: List[Dict[str, str]]
    vision_key: str
    weapon_type: str
    gender: str = ""
    title: str = ""
    nation: str = ""
    birthday: str = ""
    affiliation: str = ""
    specialDish: str = ""

    def save(self, path: str = None) -> None:
        if not os.path.exists(CHARACTER_DATA_PATH):
            os.mkdir(CHARACTER_DATA_PATH)
        file_path = os.path.join(CHARACTER_DATA_PATH, f"{path if path else self.apiname}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self, f, cls=EnhancedJSONEncoder)
        return


def get_characters() -> Tuple[set, set]:
    characters = GenshinCDN.get(path="/characters")
    fetched_characters = set()
    unfetched_characters = set()
    for character_apiname in enumerate(characters):
        if (
            character_apiname
            and character_apiname not in fetched_characters
            and character_apiname not in unfetched_characters
        ):
            character_details = GenshinCDN.get(path=f"/characters/{character_apiname}")
            if character_details:
                fetched_characters.add(character_apiname)
                character = Character(apiname=character_apiname, **character_details)
                character.save()
            else:
                unfetched_characters.add(character_apiname)
    return fetched_characters, unfetched_characters
