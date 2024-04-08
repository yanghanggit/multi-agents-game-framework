from entitas import Entity, Matcher, ExecuteProcessor #type: ignore
from auxiliary.components import (StageComponent, 
                        FightActionComponent, 
                        SpeakActionComponent,
                        TagActionComponent,
                        MindVoiceActionComponent,
                        BroadcastActionComponent,
                        WhisperActionComponent,
                        AutoPlanningComponent)
from auxiliary.actor_action import ActorPlan
from auxiliary.prompt_maker import stage_plan_prompt
from auxiliary.extended_context import ExtendedContext
from loguru import logger 

####################################################################################################    
class StagePlanningSystem(ExecuteProcessor):
    def __init__(self, context: ExtendedContext) -> None:
        self.context = context
####################################################################################################
    def execute(self) -> None:
        logger.debug("<<<<<<<<<<<<<  StagePlanningSystem  >>>>>>>>>>>>>>>>>")
        entities = self.context.get_group(Matcher(all_of=[StageComponent, AutoPlanningComponent])).entities
        for entity in entities:
            ## 开始处理场景的行为与计划
            self.handle(entity)
####################################################################################################
    def handle(self, entity: Entity) -> None:
        
        prompt = stage_plan_prompt(entity, self.context)
        agent_connect_system = self.context.agent_connect_system
        stagecomp: StageComponent = entity.get(StageComponent)
        ##
        try:
            response = agent_connect_system._request_(stagecomp.name, prompt)
            if response is None:
                logger.error(f"StagePlanSystem: response is None or empty")
                return None
            
            stageplanning = ActorPlan(stagecomp.name, response)
            for action in stageplanning.actions:
                match action.actionname:
                    case "FightActionComponent":
                        if not entity.has(FightActionComponent):
                            entity.add(FightActionComponent, action)

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
                             
                    case _:
                        logger.warning(f"error {action.actionname}, action value {action.values}")
                        continue

        except Exception as e:
            logger.exception(f"StagePlanSystem: {e}")  
            return
####################################################################################################