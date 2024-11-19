from entitas import ExecuteProcessor, Matcher, Entity, InitializeProcessor  # type: ignore
from rpg_game.rpg_entitas_context import RPGEntitasContext
from my_components.components import (
    ActorComponent,
    StageComponent,
    KickOffContentComponent,
    RoundEventsRecordComponent,
)
from typing import Set, final, override, Dict, List
import gameplay_systems.file_system_utils
from rpg_game.rpg_game import RPGGame
from extended_systems.archive_file import ActorArchiveFile, StageArchiveFile
import gameplay_systems.file_system_utils


@final
class UpdateArchiveSystem(InitializeProcessor, ExecuteProcessor):

    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

    ###############################################################################################################################################
    @override
    def initialize(self) -> None:
        all_actor_names = self._get_all_actor_names()
        all_stage_names = self._get_all_stage_names()
        self._add_kick_off_actor_archive_files(all_actor_names)
        self._add_kick_off_stage_archive_files(all_stage_names)

    ###############################################################################################################################################
    @override
    def execute(self) -> None:
        # todo
        # 自己的当前场景如果没有就加一个档案
        self._ensure_archive_for_current_stage()
        # 从本轮消息中提取出所有的档案
        self._extract_and_add_archives_from_rounds()
        self._update_appearance_of_all_actor_archives()

    ###############################################################################################################################################
    def _update_appearance_of_all_actor_archives(self) -> None:

        stage_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[StageComponent])
        ).entities

        for stage_entity in stage_entities:
            actor_entities = self._context.retrieve_actors_on_stage(stage_entity)
            if len(actor_entities) == 0:
                continue
            appearance_info = self._context.retrieve_stage_actor_appearance(
                stage_entity
            )
            for actor_entity in actor_entities:
                self._update_actor_appearance_of_archive(actor_entity, appearance_info)

    ###############################################################################################################################################
    def _update_actor_appearance_of_archive(
        self, actor_entity: Entity, appearance_info: Dict[str, str]
    ) -> None:

        my_name = self._context.safe_get_entity_name(actor_entity)
        for actor_name, actor_appearance in appearance_info.items():
            if actor_name == my_name:
                continue

            if not self._context.file_system.has_file(
                ActorArchiveFile, my_name, actor_name
            ):
                gameplay_systems.file_system_utils.register_actor_archives(
                    self._context.file_system, my_name, set({actor_name})
                )

            actor_archive = self._context.file_system.get_file(
                ActorArchiveFile, my_name, actor_name
            )
            assert actor_archive is not None
            if actor_archive.appearance != actor_appearance:
                actor_archive.set_appearance(actor_appearance)
                self._context.file_system.write_file(actor_archive)

    ###############################################################################################################################################
    def _extract_and_add_archives_from_rounds(self) -> None:

        all_actor_names = self._get_all_actor_names()
        all_stage_names = self._get_all_stage_names()

        actor_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[ActorComponent, RoundEventsRecordComponent])
        ).entities

        for actor_entity in actor_entities:

            round_events_comp = actor_entity.get(RoundEventsRecordComponent)
            messages = round_events_comp.events
            if len(messages) == 0:
                continue
            batch_content = " ".join(messages)
            self._add_actor_archive_files(actor_entity, batch_content, all_actor_names)
            self._add_stage_archive_files(actor_entity, batch_content, all_stage_names)

    ###############################################################################################################################################
    def _ensure_archive_for_current_stage(self) -> Dict[str, StageArchiveFile]:

        ret: Dict[str, StageArchiveFile] = {}

        actor_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[ActorComponent])
        ).entities

        for actor_entity in actor_entities:

            stage_entity = self._context.safe_get_stage_entity(actor_entity)
            if stage_entity is None:
                continue

            stage_name = self._context.safe_get_entity_name(stage_entity)
            actor_name = self._context.safe_get_entity_name(actor_entity)
            exist_file = self._context.file_system.get_file(
                StageArchiveFile, actor_name, stage_name
            )
            if exist_file is not None:
                continue

            new_archive = gameplay_systems.file_system_utils.register_stage_archives(
                self._context.file_system, actor_name, {stage_name}
            )

            ret[actor_name] = new_archive[0]

        return ret

    ###############################################################################################################################################
    def _add_actor_archive_files(
        self,
        entity: Entity,
        messages: str,
        optional_range_actor_names: Set[str] = set(),
    ) -> Dict[str, List[ActorArchiveFile]]:
        ret: Dict[str, List[ActorArchiveFile]] = {}

        safe_name = self._context.safe_get_entity_name(entity)
        for archive_actor_name in optional_range_actor_names:

            if safe_name == archive_actor_name:
                continue

            if archive_actor_name not in messages:
                continue

            add_archives = gameplay_systems.file_system_utils.register_actor_archives(
                self._context.file_system, safe_name, {archive_actor_name}
            )

            if len(add_archives) > 0:
                ret[safe_name] = add_archives

        return ret

    ###############################################################################################################################################
    def _add_stage_archive_files(
        self,
        entity: Entity,
        messages: str,
        optional_range_stage_names: Set[str] = set(),
    ) -> Dict[str, List[StageArchiveFile]]:
        ret: Dict[str, List[StageArchiveFile]] = {}

        safe_name = self._context.safe_get_entity_name(entity)
        for archive_stage_name in optional_range_stage_names:

            if safe_name == archive_stage_name:
                continue

            if archive_stage_name not in messages:
                continue

            add_archives = gameplay_systems.file_system_utils.register_stage_archives(
                self._context.file_system, safe_name, {archive_stage_name}
            )

            if len(add_archives) > 0:
                ret[safe_name] = add_archives

        return ret

    ###############################################################################################################################################
    def _get_all_actor_names(self) -> Set[str]:
        actor_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[ActorComponent])
        ).entities
        return {
            actor_entity.get(ActorComponent).name for actor_entity in actor_entities
        }

    ###############################################################################################################################################
    def _get_all_stage_names(self) -> Set[str]:
        stage_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[StageComponent])
        ).entities
        return {
            stage_entity.get(StageComponent).name for stage_entity in stage_entities
        }

    ###############################################################################################################################################
    def _add_kick_off_actor_archive_files(
        self, add_actor_names: Set[str]
    ) -> Dict[str, List[ActorArchiveFile]]:

        ret: Dict[str, List[ActorArchiveFile]] = {}

        actor_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[ActorComponent, KickOffContentComponent])
        ).entities

        for actor_entity in actor_entities:

            actor_comp = actor_entity.get(ActorComponent)
            kick_off_comp = actor_entity.get(KickOffContentComponent)

            for archive_actor_name in add_actor_names:
                if archive_actor_name == actor_comp.name:
                    continue

                if archive_actor_name not in kick_off_comp.content:
                    continue

                add_archives = (
                    gameplay_systems.file_system_utils.register_actor_archives(
                        self._context.file_system,
                        actor_comp.name,
                        {archive_actor_name},
                    )
                )

                if len(add_archives) > 0:
                    ret[actor_comp.name] = add_archives

        return ret

    ###############################################################################################################################################
    def _add_kick_off_stage_archive_files(
        self, add_stage_names: Set[str]
    ) -> Dict[str, List[StageArchiveFile]]:
        ret: Dict[str, List[StageArchiveFile]] = {}

        actor_entities: Set[Entity] = self._context.get_group(
            Matcher(all_of=[ActorComponent, KickOffContentComponent])
        ).entities

        for actor_entity in actor_entities:

            actor_comp = actor_entity.get(ActorComponent)
            kick_off_comp = actor_entity.get(KickOffContentComponent)

            for archive_stage_name in add_stage_names:

                if archive_stage_name == actor_comp.name:
                    continue

                if archive_stage_name not in kick_off_comp.content:
                    continue

                add_archives = (
                    gameplay_systems.file_system_utils.register_stage_archives(
                        self._context.file_system,
                        actor_comp.name,
                        {archive_stage_name},
                    )
                )

                if len(add_archives) > 0:
                    ret[actor_comp.name] = add_archives

        return ret

    ###############################################################################################################################################
