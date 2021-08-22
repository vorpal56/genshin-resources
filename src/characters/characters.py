import json
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple
from src.common.util import FileProvider, EnhancedJSONEncoder, GenshinCDN, BACKEND_PATH

CHARACTER_DATA_PATH = os.path.join(BACKEND_PATH, "characters", "data")


@dataclass
class Character(FileProvider):
    cdn_apiname: str
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
        super().save(base_path=CHARACTER_DATA_PATH, path=f"{path if path else self.apiname}")
        return


def get_characters() -> Tuple[set, set]:
    """Get a list of characters from the Genshin CDN and saves to the local directory.

    Returns:
        Tuple[set, set]: fetched_characters, unfetched_characters
    """
    characters = GenshinCDN.get(path="/characters")
    fetched_characters = set()
    unfetched_characters = set()
    for i, cdn_apiname in enumerate(characters):
        apiname = cdn_apiname.replace("-", "_")
        if apiname and apiname not in fetched_characters and apiname not in unfetched_characters:
            character_details = GenshinCDN.get(path=f"/characters/{cdn_apiname}")
            if character_details:
                fetched_characters.add(apiname)
                character = Character(apiname=apiname, cdn_apiname=cdn_apiname, **character_details)
                character.save()
                print(f"Fetched and saved {self.name}")
            else:
                unfetched_characters.add(apiname)
                print(f"Unable to fetch {self.name}")
    return fetched_characters, unfetched_characters
