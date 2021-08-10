from src.common.util import GenshinWiki, BACKEND_PATH
from enum import Enum


class AscensionGems(Enum):
    BRILLIANT_DIAMOND = "Traveler"


def get_ascension_materials():
    ascension_gems, normal_boss_materials, local_specialties = GenshinWiki.get_released_character_ascension_materials()
    print("----------------------------")
    print(ascension_gems)
    print("----------------------------")
    print(normal_boss_materials)
    print("----------------------------")
    print(local_specialties)
    print("----------------------------")