from entitas import Entity, Matcher, ExecuteProcessor #type: ignore
from auxiliary.components import (NPCComponent, 
                        FightActionComponent, 
                        SpeakActionComponent, 
                        LeaveForActionComponent, 
                        TagActionComponent, 
                        MindVoiceActionComponent,
                        BroadcastActionComponent, 
                        WhisperActionComponent,
                        SearchActionComponent,
                        AutoPlanningComponent)
from auxiliary.actor_action import ActorPlan
from auxiliary.prompt_maker import npc_plan_prompt
from auxiliary.extended_context import ExtendedContext
from loguru import logger
from typing import Optional

class NPCPlanningSystem(ExecuteProcessor):

    def __init__(self, context: ExtendedContext) -> None:
        self.context = context
####################################################################################################
    def execute(self) -> None:
        logger.debug("<<<<<<<<<<<<<  NPCPlanningSystem  >>>>>>>>>>>>>>>>>")
        entities = self.context.get_group(Matcher(all_of=[NPCComponent, AutoPlanningComponent])).entities
        for entity in entities:
            #开始处理NPC的行为计划
            self.handle(entity)
####################################################################################################
    def handle(self, entity: Entity) -> None:

        prompt = npc_plan_prompt(entity, self.context)
        npccomp: NPCComponent = entity.get(NPCComponent)

        response = self.requestplanning(npccomp.name, prompt)
        if response is None:
            logger.warning(f"NPCPlanningSystem: response is None or empty, so we can't get the planning.")
            return
        
        npcplanning = ActorPlan(npccomp.name, response)
        for action in npcplanning.actions:
            match action.actionname:
                case "FightActionComponent":
                    if not entity.has(FightActionComponent):
                        entity.add(FightActionComponent, action)

                case "LeaveForActionComponent":
                    if not entity.has(LeaveForActionComponent):
                        entity.add(LeaveForActionComponent, action)

                case "SpeakActionComponent":
                    if not entity.has(SpeakActionComponent):
                        entity.add(SpeakActionComponent, action)
                
                case "TagActionComponent":
                    if not entity.has(TagActionComponent):
                        entity.add(TagActionComponent, action)
                
                case "RememberActionComponent":
                    pass

                case "MindVoiceActionComponent":
                    if not entity.has(MindVoiceActionComponent):
                        entity.add(MindVoiceActionComponent, action)

                case "BroadcastActionComponent":
                    if not entity.has(BroadcastActionComponent):
                        entity.add(BroadcastActionComponent, action)

                case "WhisperActionComponent":
                    if not entity.has(WhisperActionComponent):
                        entity.add(WhisperActionComponent, action)

                case "SearchActionComponent":
                    if not entity.has(SearchActionComponent):
                        entity.add(SearchActionComponent, action)
                case _:
                    logger.warning(f" {action.actionname}, Unknown action name")
                    continue
####################################################################################################
    def requestplanning(self, npcname: str, prompt: str) -> Optional[str]:
        #
        context = self.context
        chaos_engineering_system = context.chaos_engineering_system
        response = chaos_engineering_system.hack_npc_planning(context, npcname, prompt)
        # 可以先走混沌工程系统
        if response is None:
           response = self.context.agent_connect_system._request_(npcname, prompt)
            
        return response
####################################################################################################