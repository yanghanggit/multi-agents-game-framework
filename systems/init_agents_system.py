from entitas import Entity, Matcher, InitializeProcessor # type: ignore
from auxiliary.components import WorldComponent, StageComponent, NPCComponent, PlayerComponent
from auxiliary.extended_context import ExtendedContext
from loguru import logger


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
class InitAgentsSystem(InitializeProcessor):
    def __init__(self, context: ExtendedContext) -> None:
        self.context: ExtendedContext = context
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
    def initialize(self) -> None:
        logger.debug("<<<<<<<<<<<<<  InitAgentsSystem  >>>>>>>>>>>>>>>>>")
        self.connect_world_agents()
        self.connect_stage_agents()
        self.connect_npc_agents()
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
    def connect_world_agents(self) -> None:
        agent_connect_system = self.context.agent_connect_system
        worlds: set[Entity] = self.context.get_group(Matcher(WorldComponent)).entities
        for world in worlds:
            worldcomp: WorldComponent = world.get(WorldComponent)
            agent_connect_system.connect_actor_agent(worldcomp.name)
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
    def connect_stage_agents(self) -> None:
        agent_connect_system = self.context.agent_connect_system
        stages: set[Entity] = self.context.get_group(Matcher(StageComponent)).entities
        for stage in stages:
            stagecomp: StageComponent = stage.get(StageComponent)
            agent_connect_system.connect_actor_agent(stagecomp.name)
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
    def connect_npc_agents(self) -> None:
        agent_connect_system = self.context.agent_connect_system
        npcs: set[Entity] = self.context.get_group(Matcher(all_of=[NPCComponent], none_of=[PlayerComponent])).entities
        for npc in npcs:
            npccomp: NPCComponent = npc.get(NPCComponent)
            agent_connect_system.connect_actor_agent(npccomp.name)
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
    