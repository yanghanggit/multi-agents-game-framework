from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from typing import final, override
from my_components.action_components import StageTagAction
from rpg_game.rpg_entitas_context import RPGEntitasContext
from rpg_game.rpg_game import RPGGame
from extended_systems.archive_file import StageArchiveFile
import gameplay_systems.file_system_utils


############################################################################################################
@final
class StageTagActionSystem(ReactiveProcessor):

    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

    ############################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(StageTagAction): GroupEvent.ADDED}

    ############################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(StageTagAction)

    ############################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        for entity in entities:
            self.update_stage_archive(entity)

    ############################################################################################################
    def update_stage_archive(self, stage_entity: Entity) -> None:
        stage_tag_action = stage_entity.get(StageTagAction)
        if len(stage_tag_action.values) == 0:
            return

        actor_entities = self._context.retrieve_actors_on_stage(stage_entity)
        for actor_entity in actor_entities:

            actor_name = self._context.safe_get_entity_name(actor_entity)

            if not self._context.file_system.has_file(
                StageArchiveFile, actor_name, stage_tag_action.name
            ):
                # 保证必须有
                gameplay_systems.file_system_utils.register_stage_archives(
                    self._context.file_system,
                    actor_name,
                    set({stage_tag_action.name}),
                )

            stage_archive = self._context.file_system.get_file(
                StageArchiveFile, actor_name, stage_tag_action.name
            )

            assert stage_archive is not None
            stage_archive.set_stage_tags(stage_tag_action.values.copy())

    ############################################################################################################