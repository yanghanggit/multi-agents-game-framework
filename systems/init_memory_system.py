from overrides import override
from entitas import Entity, Matcher, InitializeProcessor, ExecuteProcessor # type: ignore
from auxiliary.components import WorldComponent, StageComponent, NPCComponent, PlayerComponent, PerceptionActionComponent, CheckStatusActionComponent
from auxiliary.cn_builtin_prompt import (init_memory_system_prompt)
from auxiliary.extended_context import ExtendedContext
from loguru import logger
from systems.update_archive_helper import UpdareArchiveHelper
from typing import Dict
from auxiliary.actor_action import ActorAction

###############################################################################################################################################
class InitMemorySystem(InitializeProcessor, ExecuteProcessor):
    def __init__(self, context: ExtendedContext) -> None:
        self.context: ExtendedContext = context
        self.tasks: Dict[str, str] = {}
        self.flag_first_time_add_perception_and_check_status: bool = False
###############################################################################################################################################
    @override
    def initialize(self) -> None:
        context = self.context
        helper = UpdareArchiveHelper(context)
        helper.prepare()
        #分段处理
        self.tasks.clear()
        world_tasks = self.create_world_init_memory_tasks(helper)
        stage_tasks = self.create_stage_init_memory_tasks(helper)
        npc_tasks = self.create_npc_init_memory_tasks(helper)
        #
        self.tasks.update(world_tasks)
        self.tasks.update(stage_tasks)
        self.tasks.update(npc_tasks)
###############################################################################################################################################
    @override
    def execute(self) -> None:
        if not self.flag_first_time_add_perception_and_check_status:
            self.first_time_add_perception_and_check_status()
            self.flag_first_time_add_perception_and_check_status = True
####################################################################################################
    def first_time_add_perception_and_check_status(self) -> None:
        context = self.context
        entities: set[Entity] = context.get_group(Matcher(all_of=[NPCComponent], none_of=[PlayerComponent])).entities
        for entity in entities:
            npccomp: NPCComponent = entity.get(NPCComponent)
            #
            if not entity.has(PerceptionActionComponent):
                perception_action = ActorAction(npccomp.name, PerceptionActionComponent.__name__, [npccomp.current_stage])
                entity.add(PerceptionActionComponent, perception_action)
            #
            if not entity.has(CheckStatusActionComponent):
                check_status_action = ActorAction(npccomp.name, CheckStatusActionComponent.__name__, [npccomp.name])
                entity.add(CheckStatusActionComponent, check_status_action)
####################################################################################################
    @override
    async def async_execute(self) -> None:
        context = self.context
        agent_connect_system = context.agent_connect_system
        if len(self.tasks) == 0:
            #logger.error("InitMemorySystem tasks is empty.")
            return
        
        for name, prompt in self.tasks.items():
            agent_connect_system.add_async_requet_task(name, prompt)

        await context.agent_connect_system.run_async_requet_tasks("InitMemorySystem")
        self.tasks.clear() # 这句必须得走！！！
        logger.info("InitMemorySystem done.")
###############################################################################################################################################
    def create_world_init_memory_tasks(self, helper: UpdareArchiveHelper) -> Dict[str, str]:

        result: Dict[str, str] = {}

        context = self.context
        memory_system = context.memory_system
        agent_connect_system = context.agent_connect_system
        worlds: set[Entity] = context.get_group(Matcher(WorldComponent)).entities
        for world in worlds:
            worldcomp: WorldComponent = world.get(WorldComponent)
            worldmemory = memory_system.getmemory(worldcomp.name)
            if worldmemory == "":
                logger.error(f"worldmemory is empty: {worldcomp.name}")
                continue
            prompt = init_memory_system_prompt(worldmemory)
            agent_connect_system.add_async_requet_task(worldcomp.name, prompt)
            result[worldcomp.name] = prompt
        
        return result
###############################################################################################################################################
    def create_stage_init_memory_tasks(self, helper: UpdareArchiveHelper) -> Dict[str, str]:

        result: Dict[str, str] = {}

        context = self.context
        memory_system = context.memory_system
        agent_connect_system = context.agent_connect_system
        stages: set[Entity] = context.get_group(Matcher(StageComponent)).entities
        for stage in stages:
            stagecomp: StageComponent = stage.get(StageComponent)
            stagememory = memory_system.getmemory(stagecomp.name)
            if stagememory == "":
                logger.error(f"stagememory is empty: {stagecomp.name}")
                continue
            prompt = init_memory_system_prompt(stagememory)
            agent_connect_system.add_async_requet_task(stagecomp.name, prompt)
            result[stagecomp.name] = prompt
        
        return result
###############################################################################################################################################
    def create_npc_init_memory_tasks(self, helper: UpdareArchiveHelper) -> Dict[str, str]:

        result: Dict[str, str] = {}

        #
        context = self.context
        memory_system = context.memory_system
        agent_connect_system = context.agent_connect_system
        npcs: set[Entity] = context.get_group(Matcher(all_of=[NPCComponent])).entities
        for npcentity in npcs:
            npccomp: NPCComponent = npcentity.get(NPCComponent)
            npcname: str = npccomp.name
            npcmemory = memory_system.getmemory(npcname)
            if npcmemory == "":
                logger.error(f"npcmemory is empty: {npcname}")
                continue
            prompt = init_memory_system_prompt(npcmemory)
            agent_connect_system.add_async_requet_task(npcname, prompt)
            result[npcname] = prompt

        return result
###############################################################################################################################################
