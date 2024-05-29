from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent # type: ignore
from auxiliary.components import (
    LeaveForActionComponent, 
    NPCComponent,
    PlayerComponent
    )
from auxiliary.actor_action import ActorAction
from auxiliary.extended_context import ExtendedContext
from loguru import logger
from auxiliary.director_component import notify_stage_director, StageDirectorComponent
from typing import cast, Dict
from auxiliary.player_proxy import add_player_client_npc_message
from auxiliary.director_event import IDirectorEvent
from auxiliary.cn_builtin_prompt import (someone_entered_my_stage_observed_his_appearance_prompt,
                                          observe_appearance_after_entering_stage_prompt, leave_stage_prompt,
                                          enter_stage_prompt1,
                                          enter_stage_prompt2,
                                          stage_director_begin_prompt, 
                                          stage_director_end_prompt,
                                          stage_director_event_wrap_prompt)


###############################################################################################################################################
class LeaveActionHelper:

    def __init__(self, context: ExtendedContext, who_wana_leave: Entity, target_stage_name: str) -> None:
        self.context = context
        self.who_wana_leave_entity = who_wana_leave
        self.current_stage_name = cast(NPCComponent, who_wana_leave.get(NPCComponent)).current_stage
        self.current_stage_entity = self.context.getstage(self.current_stage_name)
        self.target_stage_name = target_stage_name
        self.target_stage_entity = self.context.getstage(target_stage_name)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class NPCLeaveStageEvent(IDirectorEvent):

    def __init__(self, npc_name: str, current_stage_name: str, leave_for_stage_name: str) -> None:
        self.npc_name = npc_name
        self.current_stage_name = current_stage_name
        self.leave_for_stage_name = leave_for_stage_name

    def tonpc(self, npcname: str, extended_context: ExtendedContext) -> str:
        event = leave_stage_prompt(self.npc_name, self.current_stage_name, self.leave_for_stage_name)
        return event
    
    def tostage(self, stagename: str, extended_context: ExtendedContext) -> str:
        event = leave_stage_prompt(self.npc_name, self.current_stage_name, self.leave_for_stage_name)
        return event
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class NPCEnterStageEvent(IDirectorEvent):

    def __init__(self, npc_name: str, stage_name: str, last_stage_name: str) -> None:
        self.npc_name = npc_name
        self.stage_name = stage_name
        self.last_stage_name = last_stage_name

    def tonpc(self, npcname: str, extended_context: ExtendedContext) -> str:
        if npcname != self.npc_name:
            # 目标场景内的一切听到的是这个:"xxx进入了场景"
            return enter_stage_prompt1(self.npc_name, self.stage_name)
            
        #通知我自己，我从哪里去往了哪里。这样prompt更加清晰一些
        return enter_stage_prompt2(self.npc_name, self.stage_name, self.last_stage_name)
    
    def tostage(self, stagename: str, extended_context: ExtendedContext) -> str:
        event = enter_stage_prompt1(self.npc_name, self.stage_name)
        return event    
####################################################################################################################################
####################################################################################################################################
#################################################################################################################################### 
class NPCObserveAppearanceAfterEnterStageEvent(IDirectorEvent):

    def __init__(self, who_enter_stage: str, enter_stage_name: str, all_appearance_data: Dict[str, str]) -> None:
        self.who_enter_stage = who_enter_stage
        self.enter_stage_name = enter_stage_name
        self.all_appearance_data = all_appearance_data
        #
        self.npc_appearance_in_stage = all_appearance_data.copy()
        self.npc_appearance_in_stage.pop(who_enter_stage)

    def tonpc(self, npcname: str, extended_context: ExtendedContext) -> str:
        if npcname != self.who_enter_stage:
            # 已经在场景里的人看到的是进来的人的外貌
            appearance = self.all_appearance_data.get(self.who_enter_stage, "")
            return someone_entered_my_stage_observed_his_appearance_prompt(self.who_enter_stage, appearance)

        ## 进入场景的人看到的是场景里的人的外貌
        return observe_appearance_after_entering_stage_prompt(self.who_enter_stage, self.enter_stage_name, self.npc_appearance_in_stage)
    
    def tostage(self, stagename: str, extended_context: ExtendedContext) -> str:
        return ""
####################################################################################################################################
####################################################################################################################################
#################################################################################################################################### 
class LeaveForActionSystem(ReactiveProcessor):

    def __init__(self, context: ExtendedContext) -> None:
        super().__init__(context)
        self.context = context

    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(LeaveForActionComponent): GroupEvent.ADDED}

    def filter(self, entity: Entity) -> bool:
        return entity.has(LeaveForActionComponent) and entity.has(NPCComponent)

    def react(self, entities: list[Entity]) -> None:
        self.leavefor(entities)

###############################################################################################################################################
    def leavefor(self, entities: list[Entity]) -> None:

        for entity in entities:
            if not entity.has(NPCComponent):
                logger.warning(f"LeaveForActionSystem: {entity} is not NPC?!")
                continue
            
            leavecomp: LeaveForActionComponent = entity.get(LeaveForActionComponent)
            action: ActorAction = leavecomp.action
            if len(action.values) == 0:
               continue
   
            stagename = action.values[0]
            handle = LeaveActionHelper(self.context, entity, stagename)
            if handle.target_stage_entity is None or handle.current_stage_entity is None or handle.target_stage_entity == handle.current_stage_entity:
                continue

            if handle.current_stage_entity is not None:
                #离开前的处理
                self.before_leave_stage(handle)
                #离开
                self.leave_stage(handle)

            #进入新的场景
            self.enter_stage(handle)
###############################################################################################################################################            
    def enter_stage(self, helper: LeaveActionHelper) -> None:

        entity = helper.who_wana_leave_entity
        current_stage_name = helper.current_stage_name
        target_stage_name = helper.target_stage_name
        target_stage_entity = helper.target_stage_entity
        assert target_stage_entity is not None
        npccomp: NPCComponent = entity.get(NPCComponent)

        replace_name = npccomp.name
        replace_current_stage = target_stage_name
        entity.replace(NPCComponent, replace_name, replace_current_stage)
        self.context.change_stage_tag_component(entity, current_stage_name, replace_current_stage)

        #进入场景的事件需要通知相关的人
        notify_stage_director(self.context, entity, NPCEnterStageEvent(npccomp.name, target_stage_name, current_stage_name))

        #通知一下外貌的信息
        appearancedata: Dict[str, str] = self.context.npc_appearance_in_the_stage(entity)
        if len(appearancedata) > len([entity]):
            #通知导演
            notify_stage_director(self.context, entity, NPCObserveAppearanceAfterEnterStageEvent(npccomp.name, target_stage_name, appearancedata))
###############################################################################################################################################
    def before_leave_stage(self, helper: LeaveActionHelper) -> None:
        #目前就是强行刷一下history
        self.direct_before_leave(helper)
###############################################################################################################################################
    def direct_before_leave(self, helper: LeaveActionHelper) -> None:
        #
        current_stage_entity = helper.current_stage_entity
        assert current_stage_entity is not None
        #
        directorcomp: StageDirectorComponent = current_stage_entity.get(StageDirectorComponent)
        safe_npc_name = self.context.safe_get_entity_name(helper.who_wana_leave_entity)
        #
        events2npc = directorcomp.tonpc(safe_npc_name, self.context)   

        #
        if len(events2npc) > 0:
            self.context.safe_add_human_message_to_entity(helper.who_wana_leave_entity, stage_director_begin_prompt(directorcomp.name, len(events2npc)))

        #
        # for event in events2npc:
        #     logger.debug(f"{safe_npc_name} => {event}")
        #     self.context.safe_add_human_message_to_entity(helper.who_wana_leave_entity, event)    

        ## 我希望循环events2npc遍历出每一个event，而且知道event的index.
        for index, event in enumerate(events2npc):
            wrap_prompt = stage_director_event_wrap_prompt(event, index)
            logger.debug(f"{safe_npc_name} => {event}")
            self.context.safe_add_human_message_to_entity(helper.who_wana_leave_entity, wrap_prompt)
            #logger.debug(f"Event {index}: {event}")
            # Your code here to handle each event

        #
        if len(events2npc) > 0:
            self.context.safe_add_human_message_to_entity(helper.who_wana_leave_entity, stage_director_end_prompt(directorcomp.name, len(events2npc)))

        ##
        if helper.who_wana_leave_entity.has(PlayerComponent):
            events2player = directorcomp.player_client_message(safe_npc_name, self.context)
            for event in events2player:
                add_player_client_npc_message(helper.who_wana_leave_entity, event)
    ###############################################################################################################################################
    def leave_stage(self, helper: LeaveActionHelper) -> None:
        entity: Entity = helper.who_wana_leave_entity
        npccomp: NPCComponent = entity.get(NPCComponent)
        assert helper.current_stage_entity is not None

        replace_name = npccomp.name
        replace_current_stage = "" #设置空！！！！！
        entity.replace(NPCComponent, replace_name, replace_current_stage)
        
        self.context.change_stage_tag_component(entity, helper.current_stage_name, replace_current_stage)

        notify_stage_director(self.context, entity, NPCLeaveStageEvent(npccomp.name, helper.current_stage_name, helper.target_stage_name))
    ###############################################################################################################################################
         
