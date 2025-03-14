from entitas import Entity, ExecuteProcessor  # type: ignore
from typing import final, override, List
from game.rpg_game_context import RPGGameContext
from game.rpg_game import RPGGame
from components.components import (
    PlayerActorFlagComponent,
    ActorComponent,
    StageGraphComponent,
)
from extended_systems.archive_file import StageArchiveFile
from player.player_proxy import PlayerProxy
from rpg_models.event_models import AgentEvent
from game.terminal_rpg_game import TerminalRPGGame
from loguru import logger


@final
class TerminalPlayerTipsSystem(ExecuteProcessor):
    def __init__(self, context: RPGGameContext, rpg_game: RPGGame) -> None:
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game

    ############################################################################################################
    @override
    def execute(self) -> None:
        if not isinstance(self._game, TerminalRPGGame):
            logger.debug("不是终端游戏，无法使用这个系统")
            return
        self.tips_stages()

    ############################################################################################################
    def tips_stages(self) -> None:

        for player_proxy in self._game.players:

            if player_proxy is None:
                continue

            player_entity = self._context.get_player_entity(player_proxy.name)
            if player_entity is None:
                continue

            assert player_entity is not None
            assert player_entity.has(PlayerActorFlagComponent)
            assert player_entity.has(ActorComponent)

            # 当前场景能去往的场景
            self.tips_next_stages(player_proxy, player_entity)

            # 已知的场景
            self.tip_stage_archives(player_proxy, player_entity)

    ############################################################################################################
    def tips_next_stages(
        self, player_proxy: PlayerProxy, player_entity: Entity
    ) -> None:
        assert player_entity is not None
        assert player_proxy is not None

        actor_name = self._context.safe_get_entity_name(player_entity)
        stage_entity = self._context.safe_get_stage_entity(player_entity)
        assert stage_entity is not None

        if not stage_entity.has(StageGraphComponent):
            player_proxy.add_tip_message(
                self._context.safe_get_entity_name(stage_entity),
                AgentEvent(message="当前场景没有相连接的场景，无法离开"),
            )
            return

        stage_graph_comp = stage_entity.get(StageGraphComponent)
        assert stage_graph_comp is not None

        stage_names: List[str] = [
            self.parse_stage_name(stage_name, actor_name)
            for stage_name in stage_graph_comp.stage_graph
        ]
        player_proxy.add_tip_message(
            self._context.safe_get_entity_name(stage_entity),
            AgentEvent(message=f"可去往场景:\n{'\n'.join(stage_names)}"),
        )

    ############################################################################################################
    def parse_stage_name(self, stage_name: str, actor_name: str) -> str:

        if self._context.file_system.has_file(StageArchiveFile, actor_name, stage_name):
            return stage_name

        stage_entity = self._context.get_stage_entity(stage_name)
        assert stage_entity is not None

        # assert stage_entity.has(GUIDComponent)
        # guid_comp = stage_entity.get(GUIDComponent)
        # return ComplexStageName.generate_unknown_stage_name(guid_comp.GUID)
        return stage_name

    ############################################################################################################
    def tip_stage_archives(
        self, player_proxy: PlayerProxy, player_entity: Entity
    ) -> None:

        assert player_entity is not None
        assert player_proxy is not None

        actor_name = self._context.safe_get_entity_name(player_entity)
        stage_archives = self._context.file_system.get_files(
            StageArchiveFile, actor_name
        )
        stage_names: List[str] = [
            stage_archive.name for stage_archive in stage_archives
        ]

        if len(stage_names) > 0:

            player_proxy.add_tip_message(
                actor_name,
                AgentEvent(message=f"已知场景:\n{'\n'.join(stage_names)}"),
            )
        else:
            player_proxy.add_tip_message(actor_name, AgentEvent(message="没有已知场景"))


############################################################################################################
