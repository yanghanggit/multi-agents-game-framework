from typing import final
from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from overrides import override
from gameplay_systems.action_components import (
    SpeakAction,
    BroadcastAction,
    WhisperAction,
)
from gameplay_systems.components import PlayerComponent, ActorComponent
from rpg_game.rpg_entitas_context import RPGEntitasContext
from rpg_game.rpg_game import RPGGame


#################################################################################################################################################
@final
class PostConversationActionSystem(ReactiveProcessor):
    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

    #################################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {
            Matcher(
                any_of=[SpeakAction, BroadcastAction, WhisperAction]
            ): GroupEvent.ADDED
        }

    #################################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(PlayerComponent) and entity.has(ActorComponent)

    #################################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        pass

    #################################################################################################################################################
