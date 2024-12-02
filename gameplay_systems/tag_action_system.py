from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from typing import final, override
from components.action_components import TagAction
from game.rpg_game_context import RPGGameContext
from game.rpg_game import RPGGame


####################################################################################################
@final
class TagActionSystem(ReactiveProcessor):

    def __init__(self, context: RPGGameContext, rpg_game: RPGGame) -> None:
        super().__init__(context)
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game

    ####################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(TagAction): GroupEvent.ADDED}

    ####################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(TagAction)

    ####################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        pass


####################################################################################################
