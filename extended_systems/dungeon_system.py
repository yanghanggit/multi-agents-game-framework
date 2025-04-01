from typing import List, Optional, final
from loguru import logger
from models.v_0_0_1 import StageInstance
from extended_systems.combat_system import CombatSystem
from pydantic import BaseModel


# TODO临时的，先管理下。
@final
class DungeonSystem(BaseModel):

    name: str
    levels: List[StageInstance]
    combat_system: CombatSystem = CombatSystem()
    position: int = 0

    ########################################################################################################################
    def current_level(self) -> Optional[StageInstance]:
        if len(self.levels) == 0:
            logger.warning("地下城系统为空！")
            return None

        if self.position >= len(self.levels):
            logger.warning("当前地下城关卡已经完成！")
            return None

        return self.levels[self.position]

    ########################################################################################################################
    def next_level(self) -> Optional[StageInstance]:

        if len(self.levels) == 0:
            logger.warning("地下城系统为空！")
            return None

        if self.position >= len(self.levels):
            logger.warning("当前地下城关卡已经完成！")
            return None

        return (
            self.levels[self.position + 1]
            if self.position + 1 < len(self.levels)
            else None
        )

    ########################################################################################################################
    def advance_level(self) -> bool:

        if len(self.levels) == 0:
            logger.warning("地下城系统为空！")
            return False

        if self.position >= len(self.levels):
            logger.warning("当前地下城关卡已经完成！")
            return False

        self.position += 1
        return True

    ########################################################################################################################
