from entitas import ExecuteProcessor, Matcher, Entity  # type: ignore
from typing import final, override, Set
from game.rpg_game_context import RPGGameContext
from loguru import logger
from game.rpg_game import RPGGame
from components.components import (
    WorldSystemComponent,
    ActorComponent,
    StageComponent,
    RoundEventsRecordComponent,
)
from rpg_models.event_models import GameRoundEvent
import rpg_game_systems.prompt_utils


################################################################################################################################################
def _generate_game_round_prompt(game_round: int) -> str:
    return f"""# 提示: {rpg_game_systems.prompt_utils.GeneralPromptTag.CURRENT_ROUND_TAG}:{game_round}"""


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


@final
class GameRoundSystem(ExecuteProcessor):
    ############################################################################################################
    def __init__(self, context: RPGGameContext, rpg_game: RPGGame) -> None:
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game

    ############################################################################################################
    @override
    def execute(self) -> None:

        # 每次进入这个系统就增加一个回合
        self._game._runtime_round += 1
        logger.debug(f"_runtime_game_round = {self._game.current_round}")

        #
        self._dispatch_game_round_events()

        # 清除这个临时用的数据结构
        self._reset_round_event_records()

    ############################################################################################################
    def _dispatch_game_round_events(self) -> None:

        entities: Set[Entity] = self._context.get_group(
            Matcher(any_of=[WorldSystemComponent, StageComponent, ActorComponent])
        ).entities

        self._context.notify_event(
            entities,
            GameRoundEvent(
                message=_generate_game_round_prompt(self._game.current_round)
            ),
        )

    ############################################################################################################
    def _reset_round_event_records(self) -> None:

        entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[RoundEventsRecordComponent])
        ).entities

        for entity in entities:
            rounds_comp = entity.get(RoundEventsRecordComponent)
            entity.replace(RoundEventsRecordComponent, rounds_comp.name, [])

    ############################################################################################################
