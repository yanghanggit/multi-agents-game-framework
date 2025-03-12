from entitas import ExecuteProcessor  # type: ignore
from typing import final, override
from game.tcg_game import TCGGame

# from loguru import logger


@final
class BeginSystem(ExecuteProcessor):
    ############################################################################################################
    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    ############################################################################################################
    @override
    def execute(self) -> None:
        pass
        # logger.info("BeginSystem execute")
