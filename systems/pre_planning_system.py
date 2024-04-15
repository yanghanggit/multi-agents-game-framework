from entitas import ExecuteProcessor, Matcher, Entity #type: ignore
from auxiliary.extended_context import ExtendedContext
from loguru import logger
from auxiliary.components import AutoPlanningComponent, StageComponent, NPCComponent, PlayerComponent
from enum import Enum


# 规划的策略
class PlanningStrategy(Enum):
    STRATEGY_ONLY_PLAYERS_STAGE = 1000
    STRATEGY_ALL = 2000

class PrePlanningSystem(ExecuteProcessor):

    def __init__(self, context: ExtendedContext) -> None:
        self.context: ExtendedContext = context
        self.strategy: PlanningStrategy = PlanningStrategy.STRATEGY_ALL
############################################################################################################
    def execute(self) -> None:
        logger.debug("<<<<<<<<<<<<<  PrePlanningSystem  >>>>>>>>>>>>>>>>>")
        ## player不允许做规划
        self.remove_all_players_auto_planning()
        ## 通过策略来做计划
        self.make_planning_by_strategy(self.strategy)
############################################################################################################
    def make_planning_by_strategy(self, strategy: PlanningStrategy) -> None:
        if strategy == PlanningStrategy.STRATEGY_ONLY_PLAYERS_STAGE:
            # 选择比较省的策略。
            playerentities = self.context.get_group(Matcher(PlayerComponent)).entities
            for playerentity in playerentities:
                # 如果有多个player在同一个stage，这里会多次执行, 但是没关系，因为这里是做防守的
                self.strategy1_only_the_stage_where_player_is_located_and_the_npcs_in_it_allowed_make_plans(playerentity)
        elif strategy == PlanningStrategy.STRATEGY_ALL:
            ## 选择比较费的策略，全都更新
            self.strategy2_all_stages_and_npcs_except_player_allow_auto_planning()   
############################################################################################################
    def remove_all_players_auto_planning(self) -> None:
        playerentities = self.context.get_group(Matcher(PlayerComponent)).entities
        for playerentity in playerentities:
            if playerentity.has(AutoPlanningComponent):
                playerentity.remove(AutoPlanningComponent)
############################################################################################################
    def strategy1_only_the_stage_where_player_is_located_and_the_npcs_in_it_allowed_make_plans(self, playerentity: Entity) -> None:
        assert playerentity is not None
        assert playerentity.has(PlayerComponent)

        context = self.context
        stageentity = context.safe_get_stage_entity(playerentity)
        if stageentity is None:
            logger.error("stage is None, player无所在场景是有问题的")
            return
        
        ##player所在场景可以规划
        stagecomp: StageComponent = stageentity.get(StageComponent)
        if not stageentity.has(AutoPlanningComponent):
            stageentity.add(AutoPlanningComponent, stagecomp.name)
        
        ###player所在场景的npcs可以规划
        npcsentities = context.npcs_in_this_stage(stagecomp.name)
        for npcentity in npcsentities:
            if npcentity.has(PlayerComponent):
                ## 挡掉
                continue
            npccomp: NPCComponent = npcentity.get(NPCComponent)
            if not npcentity.has(AutoPlanningComponent):
                npcentity.add(AutoPlanningComponent, npccomp.name)
############################################################################################################
    def strategy2_all_stages_and_npcs_except_player_allow_auto_planning(self) -> None:
        context = self.context
        stageentities = context.get_group(Matcher(StageComponent)).entities
        for stageentity in stageentities:
            stagecomp: StageComponent = stageentity.get(StageComponent)
            if not stageentity.has(AutoPlanningComponent):
                stageentity.add(AutoPlanningComponent, stagecomp.name)
        
        npcentities = context.get_group(Matcher(NPCComponent)).entities
        for npcentity in npcentities:
            if npcentity.has(PlayerComponent):
                ## player 就跳过
                continue
            npccomp: NPCComponent = npcentity.get(NPCComponent)
            if not npcentity.has(AutoPlanningComponent):
                npcentity.add(AutoPlanningComponent, npccomp.name)
############################################################################################################

