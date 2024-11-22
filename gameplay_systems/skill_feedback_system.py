from entitas import Matcher, ReactiveProcessor, GroupEvent, Entity  # type: ignore
from my_components.action_components import DamageAction
from my_components.components import (
    AttributesComponent,
    ActorComponent,
    StageComponent,
)
from rpg_game.rpg_entitas_context import RPGEntitasContext
from typing import final, override
from rpg_game.rpg_game import RPGGame
from loguru import logger


@final
class SkillFeedbackSystem(ReactiveProcessor):

    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

    ######################################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(DamageAction): GroupEvent.ADDED}

    ######################################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return (
            entity.has(DamageAction)
            and entity.has(AttributesComponent)
            and (entity.has(StageComponent) or entity.has(ActorComponent))
        )

    ######################################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        for entity in entities:
            self._test(entity)

    ######################################################################################################################################################
    def _test(self, target_entity: Entity) -> None:
        safe_name = self._context.safe_get_entity_name(target_entity)
        logger.debug(f"SkillFeedbackSystem: {safe_name} is feed back.")

    ######################################################################################################################################################
