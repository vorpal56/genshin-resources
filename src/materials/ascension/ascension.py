import os
from src.common.util import FileProvider, GenshinWiki, BACKEND_PATH
from typing import Tuple

ASCENSION_MATERIALS_PATH = os.path.join(BACKEND_PATH, "materials", "ascension", "data")


class Materials(FileProvider):
    def __init__(self, data: dict):
        self.data = data
        return

    def save(self, **kwargs) -> None:
        super().save(data=self.data, **kwargs)
        return


def get_ascension_materials() -> Tuple[dict, dict, dict]:
    materials = GenshinWiki.get_released_character_ascension_materials()
    ascension_gems, normal_boss_materials, local_specialties = materials
    Materials(data=ascension_gems).save(
        base_path=ASCENSION_MATERIALS_PATH,
        path="ascension_gems",
    )
    Materials(data=normal_boss_materials).save(base_path=ASCENSION_MATERIALS_PATH, path="boss_materials")
    Materials(data=local_specialties).save(base_path=ASCENSION_MATERIALS_PATH, path="local_specialties")
    return materials
