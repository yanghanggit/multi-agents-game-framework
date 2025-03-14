from entitas import Entity, ExecuteProcessor  # type: ignore
from typing import final, override, List
from game.rpg_game_context import RPGGameContext
from game.rpg_game import RPGGame
from components.components import (
    PlayerActorFlagComponent,
    ActorComponent,
)
from player.player_proxy import PlayerProxy
from rpg_models.event_models import AgentEvent
from game.web_rpg_game import WebRPGGame
from loguru import logger
from extended_systems.archive_file import StageArchiveFile
from components.components import (
    PlayerActorFlagComponent,
    ActorComponent,
    StageGraphComponent,
)


@final
class WebPlayerTipsSystem(ExecuteProcessor):
    def __init__(self, context: RPGGameContext, rpg_game: RPGGame) -> None:
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game
        self._test_index: int = 0

    ############################################################################################################
    @override
    def execute(self) -> None:
        if not isinstance(self._game, WebRPGGame):
            logger.debug("不是终端游戏，无法使用这个系统")
            return

        self._add_tips()

    ############################################################################################################
    def _add_tips(self) -> None:

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
            # self._add_test_tips(player_proxy, player_entity)

    ############################################################################################################
    def _add_test_tips(self, player_proxy: PlayerProxy, player_entity: Entity) -> None:
        assert player_entity is not None
        assert player_proxy is not None

        self._test_index += 1
        actor_name = self._context.safe_get_entity_name(player_entity)
        player_proxy.add_tip_message(
            actor_name,
            AgentEvent(message=f"这是一个测试的消息{self._test_index}"),
        )

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
