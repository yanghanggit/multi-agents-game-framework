from entitas import Entity  # type: ignore
from my_components.components import (
    StageComponent,
    StageEnvironmentComponent,
)
from my_components.action_components import (
    StageNarrateAction,
)
from my_agent.agent_plan import AgentPlanResponse
from rpg_game.rpg_entitas_context import RPGEntitasContext


######################################################################################################################################################
def apply_stage_narration(
    context: RPGEntitasContext, plan_response: AgentPlanResponse
) -> None:

    stage_narrate_action = plan_response.get_action(StageNarrateAction.__name__)
    if stage_narrate_action is None or len(stage_narrate_action.values) == 0:
        return

    stage_entity = context.get_entity_by_name(plan_response.agent_name)
    if stage_entity is None or not stage_entity.has(StageEnvironmentComponent):
        return

    extract_content = " ".join(stage_narrate_action.values)
    stage_entity.replace(
        StageEnvironmentComponent, plan_response.agent_name, extract_content
    )


######################################################################################################################################################
def extract_current_stage_narrative(context: RPGEntitasContext, entity: Entity) -> str:
    stage_entity = context.safe_get_stage_entity(entity)
    if stage_entity is None:
        return ""
    assert stage_entity.has(StageComponent), "stage_entity error"
    assert stage_entity.has(StageEnvironmentComponent), "stage_entity error"
    return stage_entity.get(StageEnvironmentComponent).narrate


#############################################################################################################################