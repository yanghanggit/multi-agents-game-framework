from enum import IntEnum, unique
from typing import Dict, List, final
from loguru import logger
from pydantic import BaseModel


###############################################################################################################################################
# 表示战斗的状态 Phase
@final
@unique
class CombatPhase(IntEnum):
    NONE = (0,)
    PREPARATION = (1,)  # 初始化，需要同步一些数据与状态
    ONGOING = (2,)  # 运行中，不断进行战斗推理
    COMPLETE = 3  # 结束，需要进行结算
    POST_WAIT = 4  # 战斗等待进入新一轮战斗或者回家


###############################################################################################################################################
# 表示战斗的状态
@final
@unique
class CombatResult(IntEnum):
    NONE = (0,)
    HERO_WIN = (1,)  # 胜利
    HERO_LOSE = (2,)  # 失败


###############################################################################################################################################


# 表示一个回合
class Round(BaseModel):
    tag: str
    round_turns: List[str] = []
    select_report: Dict[str, str] = {}
    stage_director_calculation: str = ""
    stage_director_performance: str = ""
    feedback_report: Dict[str, str] = {}


###############################################################################################################################################
# 表示一个战斗
class Combat(BaseModel):

    name: str
    phase: CombatPhase = CombatPhase.NONE
    result: CombatResult = CombatResult.NONE
    rounds: List[Round] = []
    summarize_report: Dict[str, str] = {}


###############################################################################################################################################
# 表示战斗系统
@final
class CombatSystem(BaseModel):

    combats: List[Combat] = []

    ###############################################################################################################################################
    @property
    def last_combat(self) -> Combat:
        assert len(self.combats) > 0
        if len(self.combats) == 0:
            return Combat(name="")

        return self.combats[-1]

    ###############################################################################################################################################
    @property
    def rounds(self) -> List[Round]:
        return self.last_combat.rounds

    ###############################################################################################################################################
    @property
    def last_round(self) -> Round:
        assert len(self.rounds) > 0
        if len(self.rounds) == 0:
            return Round(tag="")

        return self.rounds[-1]

    ###############################################################################################################################################
    def new_round(self) -> Round:
        round = Round(tag=f"round_{len(self.last_combat.rounds) + 1}")
        self.last_combat.rounds.append(round)
        logger.debug(f"新的回合开始 = {len(self.last_combat.rounds)}")
        return round

    ###############################################################################################################################################
    @property
    def is_on_going_phase(self) -> bool:
        return self.last_combat.phase == CombatPhase.ONGOING

    ###############################################################################################################################################
    @property
    def is_complete_phase(self) -> bool:
        return self.last_combat.phase == CombatPhase.COMPLETE

    ###############################################################################################################################################
    @property
    def is_preparation_phase(self) -> bool:
        return self.last_combat.phase == CombatPhase.PREPARATION

    ###############################################################################################################################################
    @property
    def is_post_wait_phase(self) -> bool:
        return self.last_combat.phase == CombatPhase.POST_WAIT

    ###############################################################################################################################################
    @property
    def combat_result(self) -> CombatResult:
        return self.last_combat.result

    ###############################################################################################################################################
    # 启动一个战斗！！！ 注意状态转移
    def combat_engagement(self, combat: Combat) -> None:
        assert combat.phase == CombatPhase.NONE
        combat.phase = CombatPhase.PREPARATION
        self.combats.append(combat)

    ###############################################################################################################################################
    def combat_go(self) -> None:
        assert self.last_combat.phase == CombatPhase.PREPARATION
        assert self.last_combat.result == CombatResult.NONE
        self.last_combat.phase = CombatPhase.ONGOING

    ###############################################################################################################################################
    def combat_complete(self, result: CombatResult) -> None:
        # 设置战斗结束阶段！
        assert self.last_combat.phase == CombatPhase.ONGOING
        assert result == CombatResult.HERO_WIN or result == CombatResult.HERO_LOSE
        assert self.last_combat.result == CombatResult.NONE

        # "战斗已经结束"
        self.last_combat.phase = CombatPhase.COMPLETE
        # 设置战斗结果！
        self.last_combat.result = result

    ###############################################################################################################################################
    def combat_post_wait(self) -> None:
        assert (
            self.last_combat.result == CombatResult.HERO_WIN
            or self.last_combat.result == CombatResult.HERO_LOSE
        )
        assert self.last_combat.phase == CombatPhase.COMPLETE

        # 设置战斗等待阶段！
        self.last_combat.phase = CombatPhase.POST_WAIT

    ###############################################################################################################################################
