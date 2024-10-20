from entitas import Matcher, InitializeProcessor  # type: ignore
from typing import final, override
from gameplay_systems.components import WorldComponent, StageComponent, ActorComponent
from rpg_game.rpg_entitas_context import RPGEntitasContext
from rpg_game.rpg_game import RPGGame


@final
class ConnectAgentSystem(InitializeProcessor):
    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

    ###############################################################################################################################################
    @override
    def initialize(self) -> None:
        self.connect_world_system_agents()
        self.connect_stage_agents()
        self.connect_actor_agents()

    ###############################################################################################################################################
    def connect_world_system_agents(self) -> None:
        world_entities = self._context.get_group(Matcher(WorldComponent)).entities
        for world_entity in world_entities:
            world_comp = world_entity.get(WorldComponent)
            self._context._langserve_agent_system.connect_agent(world_comp.name)

    ###############################################################################################################################################
    def connect_stage_agents(self) -> None:
        stage_entities = self._context.get_group(Matcher(StageComponent)).entities
        for stage_entity in stage_entities:
            stage_comp = stage_entity.get(StageComponent)
            self._context._langserve_agent_system.connect_agent(stage_comp.name)

    ###############################################################################################################################################
    def connect_actor_agents(self) -> None:
        actor_entities = self._context.get_group(Matcher(ActorComponent)).entities
        for actor_entity in actor_entities:
            actor_comp = actor_entity.get(ActorComponent)
            self._context._langserve_agent_system.connect_agent(actor_comp.name)


###############################################################################################################################################
