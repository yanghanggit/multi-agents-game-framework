from typing import override
from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent # type: ignore
from ecs_systems.action_components import (GoToActionComponent, PortalStepActionComponent, DeadActionComponent)
from ecs_systems.components import ActorComponent, ExitOfPortalComponent
from my_agent.agent_action import AgentAction
from my_entitas.extended_context import ExtendedContext
from loguru import logger

###############################################################################################################################################
class PortalStepActionSystem(ReactiveProcessor):

    def __init__(self, context: ExtendedContext) -> None:
        super().__init__(context)
        self._context = context
###############################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(PortalStepActionComponent): GroupEvent.ADDED}
###############################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(PortalStepActionComponent) and entity.has(ActorComponent) and not entity.has(DeadActionComponent)
###############################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
         for entity in entities:
            self.portalstep(entity)
###############################################################################################################################################
    def portalstep(self, entity: Entity) -> None:
        
        actor_comp: ActorComponent = entity.get(ActorComponent)
        portalstepcomp: PortalStepActionComponent = entity.get(PortalStepActionComponent)
        action: AgentAction = portalstepcomp.action
        stage_name = action.value(0)
        if stage_name == "":
            logger.error(f"PortalStepActionSystem: {actor_comp.name} 想要离开的场景是: {stage_name}")
            return
        
        logger.debug(f"PortalStepActionSystem: {actor_comp.name} 想要离开的场景是: {stage_name}")
        if stage_name != actor_comp.current_stage:
            # 只能脱离当前场景
            logger.error(f"PortalStepActionSystem: {actor_comp.name} 只能脱离当前场景 {actor_comp.current_stage}, 但是action里的场景对不上 {stage_name}")
            return

        # 取出当前场景
        stageentity = self._context.get_stage_entity(stage_name)
        assert stageentity is not None, f"PortalStepActionSystem: {stage_name} is None"
        if not stageentity.has(ExitOfPortalComponent):
            # 该场景没有连接到任何场景，所以不能"盲目"的离开
            logger.error(f"PortalStepActionSystem: {actor_comp.name} 想要离开的场景是: {stage_name}, 该场景没有连接到任何场景")
            return
        
        # 取出数据，并准备沿用GoToActionComponent
        exit_of_portal_comp: ExitOfPortalComponent = stageentity.get(ExitOfPortalComponent)
        logger.debug(f"PortalStepActionSystem: {actor_comp.name} 想要离开的场景是: {stage_name}, 该场景可以连接的场景有: {exit_of_portal_comp.name}")
        target_stage_entity = self._context.get_stage_entity(exit_of_portal_comp.name)
        if target_stage_entity is None:
            logger.error(f"PortalStepActionSystem: {actor_comp.name} 想要离开的场景是: {stage_name}, 该场景可以连接的场景有: {exit_of_portal_comp.name}, 但是该场景不存在")
            return
        
        logger.debug(f"{exit_of_portal_comp.name}允许{actor_comp.name}前往")
        
        # 生成离开当前场景的动作
        entity.add(GoToActionComponent, AgentAction(actor_comp.name, GoToActionComponent.__name__, [exit_of_portal_comp.name]))
###############################################################################################################################################       

            
