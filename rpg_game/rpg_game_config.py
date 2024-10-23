from enum import StrEnum
from typing import List


class RPGGameConfig(StrEnum):

    WORLD_APPEARANCE_SYSTEM_NAME = "角色外观生成器"

    WORLD_SKILL_SYSTEM_NAME = "技能系统"

    GAME_SAMPLE_RUNTIME_DIR = "game_sample/gen_runtimes"

    GAME_ARCHIVE_DIR = "game_archive"

    CHECK_GAME_RESOURCE_VERSION = "0.0.1"


# 临时
GEN_GAMES: List[str] = ["World1", "World2", "World3"]
