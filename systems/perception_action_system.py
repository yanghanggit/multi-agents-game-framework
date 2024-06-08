from entitas import ReactiveProcessor, Matcher, GroupEvent, Entity #type: ignore
from auxiliary.extended_context import ExtendedContext
from auxiliary.components import (  PerceptionActionComponent,
                                    StageComponent,
                                    AppearanceComponent,
                                    DeadActionComponent,
                                    ActorComponent)
from loguru import logger
from typing import List, Dict, override
from auxiliary.director_component import notify_stage_director
from auxiliary.director_event import IDirectorEvent
from auxiliary.cn_builtin_prompt import perception_action_prompt

####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PerceptionActionHelper:

    def __init__(self, context: ExtendedContext):
        self.context = context
        self.props_in_stage: List[str] = []
        self.actors_in_stage: Dict[str, str] = {}
###################################################################################################################
    def perception(self, entity: Entity) -> None:
        safestage = self.context.safe_get_stage_entity(entity)
        if safestage is None:
            logger.error(f"PerceptionActionHelper: {self.context.safe_get_entity_name(entity)} can't find the stage")
            return
        self.actors_in_stage = self.perception_actors_in_stage(entity, safestage)
        self.props_in_stage = self.perception_props_in_stage(entity, safestage)
###################################################################################################################
    def perception_actors_in_stage(self, entity: Entity, stageentity: Entity) -> Dict[str, str]:
        res: Dict[str, str] = {}
        stagecomp: StageComponent = stageentity.get(StageComponent)
        actor_entites = self.context.actors_in_stage(stagecomp.name)
        for _en in actor_entites:
            if _en == entity:
                continue
            actor_comp: ActorComponent = _en.get(ActorComponent)
            appearance_comp: AppearanceComponent  = _en.get(AppearanceComponent)
            res[actor_comp.name] = appearance_comp.appearance
        return res
###################################################################################################################
    def perception_props_in_stage(self, entity: Entity, stageentity: Entity) -> List[str]:
        res: List[str] = []
        stagecomp: StageComponent = stageentity.get(StageComponent)
        props_in_stage = self.context.file_system.get_prop_files(stagecomp.name)
        for prop in props_in_stage:
            res.append(prop.name)
        return res
####################################################################################################################################
####################################################################################################################################
#################################################################################################################################### 
class ActorPerceptionEvent(IDirectorEvent):

    def __init__(self, who_perception: str, stagename: str, result_actors_in_stage: Dict[str, str], result_props_in_stage: List[str]) -> None:
        self.who_perception = who_perception
        self.stagename = stagename
        self.result_actors_in_stage = result_actors_in_stage
        self.result_props_in_stage = result_props_in_stage
    
    def to_actor(self, actor_name: str, extended_context: ExtendedContext) -> str:
        if actor_name != self.who_perception:
            return ""
        return perception_action_prompt(self.who_perception, self.stagename, self.result_actors_in_stage, self.result_props_in_stage)
    
    def to_stage(self, stagename: str, extended_context: ExtendedContext) -> str:
        return ""
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PerceptionActionSystem(ReactiveProcessor):

    def __init__(self, context: ExtendedContext):
        super().__init__(context)
        self.context = context
###################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return { Matcher(PerceptionActionComponent): GroupEvent.ADDED }
###################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(PerceptionActionComponent) and entity.has(ActorComponent) and not entity.has(DeadActionComponent)
###################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        for entity in entities:
            self.perception(entity)
###################################################################################################################
    def perception(self, entity: Entity) -> None:
        safe_name = self.context.safe_get_entity_name(entity)
        #
        helper = PerceptionActionHelper(self.context)
        helper.perception(entity)
        #
        stageentity = self.context.safe_get_stage_entity(entity)
        assert stageentity is not None
        safe_stage_name = self.context.safe_get_entity_name(stageentity)   
        notify_stage_director(self.context, entity, ActorPerceptionEvent(safe_name, safe_stage_name, helper.actors_in_stage, helper.props_in_stage))
###################################################################################################################
