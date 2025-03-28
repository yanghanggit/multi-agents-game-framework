from entitas import ExecuteProcessor, Matcher  # type: ignore
from typing import final, override
from game.tcg_game import TCGGame
from components.components_v_0_0_1 import (
    StagePermitComponent,
    ActorPermitComponent,
)


@final
class PostPlanningSystem(ExecuteProcessor):

    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    ############################################################################################################
    @override
    def execute(self) -> None:
        self._remove_all_permits()

    ############################################################################################################
    def _remove_all_permits(self) -> None:
        actor_entities = self._game.get_group(
            Matcher(
                all_of=[
                    ActorPermitComponent,
                ],
            )
        ).entities.copy()
        for entity in actor_entities:
            entity.remove(ActorPermitComponent)

        stage_entities = self._game.get_group(
            Matcher(
                all_of=[
                    StagePermitComponent,
                ]
            )
        ).entities.copy()
        for entity in stage_entities:
            entity.remove(StagePermitComponent)
