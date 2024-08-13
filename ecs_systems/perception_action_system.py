from entitas import ReactiveProcessor, Matcher, GroupEvent, Entity #type: ignore
from rpg_game.rpg_entitas_context import RPGEntitasContext
from ecs_systems.components import (StageComponent, ActorComponent)
from ecs_systems.action_components import PerceptionAction, DeadAction
from loguru import logger
from typing import List, Dict, override
from ecs_systems.stage_director_component import StageDirectorComponent
from ecs_systems.stage_director_event import IStageDirectorEvent
from ecs_systems.cn_builtin_prompt import perception_action_prompt
from file_system.files_def import PropFile

####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PerceptionActionHelper:

    """
    辅助的类，把常用的行为封装到这里，方便别的地方再调用
    """

    def __init__(self, context: RPGEntitasContext):
        self._context: RPGEntitasContext = context
        self._props_in_stage: List[str] = []
        self._actors_in_stage: Dict[str, str] = {}
###################################################################################################################
    def perception(self, entity: Entity) -> None:
        safestage = self._context.safe_get_stage_entity(entity)
        if safestage is None:
            logger.error(f"PerceptionActionHelper: {self._context.safe_get_entity_name(entity)} can't find the stage")
            return
        self._actors_in_stage = self.perception_actors_in_stage(entity, safestage)
        self._props_in_stage = self.perception_props_in_stage(entity, safestage)
###################################################################################################################
    def perception_actors_in_stage(self, entity: Entity, stageentity: Entity) -> Dict[str, str]:
        all: Dict[str, str] = self._context.appearance_in_stage(entity)
        safe_name = self._context.safe_get_entity_name(entity)
        all.pop(safe_name, None) # 删除自己，自己是不必要的。
        assert all.get(safe_name) is None
        return all
###################################################################################################################
    def perception_props_in_stage(self, entity: Entity, stageentity: Entity) -> List[str]:
        res: List[str] = []
        stagecomp: StageComponent = stageentity.get(StageComponent)
        prop_files = self._context._file_system.get_files(PropFile, stagecomp.name)
        for prop in prop_files:
            res.append(prop._name)
        return res
####################################################################################################################################
####################################################################################################################################
#################################################################################################################################### 
class ActorPerceptionEvent(IStageDirectorEvent):

    """
    感知的结果事件
    """

    def __init__(self, who: str, current_stage_name: str, actors_in_stage: Dict[str, str], props_in_stage: List[str]) -> None:
        self._who: str = who
        self._current_stage_name: str = current_stage_name
        self._actors_in_stage: Dict[str, str] = actors_in_stage
        self._props_in_stage: List[str] = props_in_stage
    
    def to_actor(self, actor_name: str, extended_context: RPGEntitasContext) -> str:
        if actor_name != self._who:
            return "" # 不是自己，不显示
        return perception_action_prompt(self._who, self._current_stage_name, self._actors_in_stage, self._props_in_stage)
    
    def to_stage(self, stagename: str, extended_context: RPGEntitasContext) -> str:
        return "" # 不显示给场景
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PerceptionActionSystem(ReactiveProcessor):

    """
    处理PerceptionActionComponent行为的系统
    """

    def __init__(self, context: RPGEntitasContext):
        super().__init__(context)
        self._context: RPGEntitasContext = context
###################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return { Matcher(PerceptionAction): GroupEvent.ADDED }
###################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(PerceptionAction) and entity.has(ActorComponent) and not entity.has(DeadAction)
###################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        for entity in entities:
            self.perception(entity)
###################################################################################################################
    def perception(self, entity: Entity) -> None:
        safe_name = self._context.safe_get_entity_name(entity)
        #
        helper = PerceptionActionHelper(self._context)
        helper.perception(entity)
        #
        stageentity = self._context.safe_get_stage_entity(entity)
        assert stageentity is not None
        safe_stage_name = self._context.safe_get_entity_name(stageentity)   
        StageDirectorComponent.add_event_to_stage_director(self._context, entity, ActorPerceptionEvent(safe_name, safe_stage_name, helper._actors_in_stage, helper._props_in_stage))
###################################################################################################################
