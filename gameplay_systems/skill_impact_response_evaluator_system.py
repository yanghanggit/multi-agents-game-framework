from entitas import Matcher, ReactiveProcessor, GroupEvent, Entity  # type: ignore
from my_components.action_components import (
    SkillAction,
    DamageAction,
    BroadcastAction,
    TagAction,
)
from my_components.components import (
    AttributesComponent,
    ActorComponent,
)
from rpg_game.rpg_entitas_context import RPGEntitasContext
from typing import final, override, List, Optional
import gameplay_systems.builtin_prompt_util as builtin_prompt_util
from my_agent.agent_task import AgentTask
from my_agent.agent_plan import AgentPlanResponse
import my_format_string.target_and_message_format_string
import my_format_string.attrs_format_string
from rpg_game.rpg_game import RPGGame
from my_models.entity_models import AttributesIndex
from my_models.event_models import AgentEvent
from loguru import logger
import gameplay_systems.skill_system_utils

################################################################################################################################################


def _generate_skill_impact_response_prompt(
    actor_name: str,
    target_name: str,
    reasoning_sentence: str,
    result_desc: str,
) -> str:

    prompt = f"""# {actor_name} 向 {target_name} 发动技能。
## 事件描述
 {reasoning_sentence}

## 系统判断结果
{result_desc}

## 判断步骤
第1步:回顾 {target_name} 的当前状态。
第2步:结合 事件描述 与 系统判断结果，推理技能对 {target_name} 的影响。例如改变你的状态，或者对你造成伤害等。
第3步:更新 {target_name} 的状态，作为最终输出。

## 输出要求
- 请遵循 输出格式指南。
- 返回结果只带如下的键: {BroadcastAction.__name__} 和 {TagAction.__name__}。
- {BroadcastAction.__name__} 的内容格式要求为: "{target_name}对技能的反馈与更新后的状态描述"。
"""

    return prompt


################################################################################################################################################


def _generate_offline_prompt(
    actor_name: str, target_name: str, reasoning_sentence: str
) -> str:

    prompt = f"""# 注意! {actor_name} 无法对 {target_name} 使用技能，本次技能释放被系统取消。
## 行动内容语句({actor_name} 发起)
{reasoning_sentence}
"""
    return prompt


################################################################################################################################################


def _generate_broadcast_skill_impact_response_prompt(
    actor_name: str, target_name: str, reasoning_sentence: str, feedback_sentence: str
) -> str:

    ret_prompt = f"""# 注意场景内发生了如下事件: {actor_name} 向 {target_name} 发动了技能。

## 技能发动的过程描述
{reasoning_sentence}

## {target_name} 受到技能后的反馈
{feedback_sentence}"""

    return ret_prompt


################################################################################################################################################
@final
class SkillImpactResponse(AgentPlanResponse):

    @property
    def impact_result(self) -> str:
        return self._concatenate_values(BroadcastAction.__name__)


################################################################################################################################################


@final
class SkillImpactResponseEvaluatorSystem(ReactiveProcessor):

    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        super().__init__(context)

        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game
        self._react_entities_copy: List[Entity] = []

    ######################################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(SkillAction): GroupEvent.ADDED}

    ######################################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(
            ActorComponent
        ) and gameplay_systems.skill_system_utils.has_skill_system_action(entity)

    ######################################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        self._react_entities_copy = entities.copy()

    ######################################################################################################################################################
    @override
    async def a_execute2(self) -> None:

        for entity in self._react_entities_copy:
            await self._process_skill_impact(entity)

        self._react_entities_copy.clear()

    ######################################################################################################################################################
    async def _process_skill_impact(self, entity: Entity) -> None:
        # 释放技能
        for (
            target
        ) in gameplay_systems.skill_system_utils.parse_skill_target_from_action(
            self._context, entity
        ):

            task = self._generate_skill_impact_response_task(entity, target)
            if task is None:
                self._on_skill_target_agent_off_line_event(entity, target)
                continue

            if task.request() is None:
                self._on_skill_target_agent_off_line_event(entity, target)
                continue

            # 加入伤害计算的逻辑
            self._evaluate_and_apply_action(entity, target)

            # 场景事件
            response_plan = SkillImpactResponse(task.agent_name, task.response_content)
            self._on_broadcast_skill_impact_response_event(
                entity, target, response_plan.impact_result
            )

    ######################################################################################################################################################
    def _on_broadcast_skill_impact_response_event(
        self, from_entity: Entity, target_entity: Entity, target_feedback: str
    ) -> None:

        current_stage_entity = self._context.safe_get_stage_entity(from_entity)
        if current_stage_entity is None:
            return

        inspector_tag, inspector_content = (
            gameplay_systems.skill_system_utils.parse_skill_world_harmony_inspector_action(
                from_entity
            )
        )
        logger.debug(f"world_skill_system_rule_tag: {inspector_tag}")

        self._context.broadcast_event_in_stage(
            current_stage_entity,
            AgentEvent(
                message=_generate_broadcast_skill_impact_response_prompt(
                    self._context.safe_get_entity_name(from_entity),
                    self._context.safe_get_entity_name(target_entity),
                    inspector_content,
                    target_feedback,
                )
            ),
            set({target_entity}),  # 已经参与的双方不需要再被通知了。
        )

    ######################################################################################################################################################
    def _evaluate_and_apply_action(self, entity: Entity, target: Entity) -> None:

        # 拿到原始的
        calculate_attrs: List[int] = self._calculate_skill_attributes(entity)
        # 补充上发起者的攻击值
        self._calculate_attr_component(entity, target, calculate_attrs)
        # 补充上所有参与的道具的属性
        self._calculate_skill_accessory_props(entity, target, calculate_attrs)
        # 最终添加到目标的伤害
        self._apply_damage(
            entity, target, calculate_attrs, self._determine_damage_bonus(entity)
        )

    ######################################################################################################################################################
    def _apply_damage(
        self, entity: Entity, target: Entity, skill_attrs: List[int], buff: float = 1.0
    ) -> None:

        skill_attrs[AttributesIndex.DAMAGE.value] = int(
            skill_attrs[AttributesIndex.DAMAGE.value] * buff
        )

        if skill_attrs[AttributesIndex.DAMAGE.value] == 0:
            return

        target.replace(
            DamageAction,
            self._context.safe_get_entity_name(target),
            [],
        )

        target.get(DamageAction).values.append(
            my_format_string.target_and_message_format_string.make_target_and_message(
                self._context.safe_get_entity_name(entity),
                my_format_string.attrs_format_string.from_int_attrs_to_string(
                    skill_attrs
                ),
            )
        )

    ######################################################################################################################################################
    def _calculate_attr_component(
        self, entity: Entity, target: Entity, out_put_skill_attrs: List[int]
    ) -> None:

        if not entity.has(AttributesComponent):
            return

        rpg_attr_comp = entity.get(AttributesComponent)
        out_put_skill_attrs[AttributesIndex.DAMAGE.value] += rpg_attr_comp.attack

    ######################################################################################################################################################
    def _calculate_skill_accessory_props(
        self, entity: Entity, target: Entity, out_put_skill_attrs: List[int]
    ) -> None:

        data = gameplay_systems.skill_system_utils.parse_skill_accessory_prop_info_from_action(
            self._context, entity
        )
        for prop_file_and_count_data in data:
            for i in range(len(out_put_skill_attrs)):
                prop_file = prop_file_and_count_data[0]
                count = prop_file_and_count_data[1]
                out_put_skill_attrs[i] += prop_file.prop_model.attributes[i] * count

    ######################################################################################################################################################
    def _calculate_skill_attributes(self, entity: Entity) -> List[int]:
        final_attr: List[int] = []
        for (
            skill_prop_file
        ) in gameplay_systems.skill_system_utils.parse_skill_prop_files_from_action(
            self._context, entity
        ):
            if len(final_attr) == 0:
                final_attr = skill_prop_file.prop_model.attributes
            else:
                for i in range(len(final_attr)):
                    final_attr[i] += skill_prop_file.prop_model.attributes[i]
        return final_attr

    ######################################################################################################################################################
    def _on_skill_target_agent_off_line_event(
        self, entity: Entity, target: Entity
    ) -> None:

        world_skill_system_rule_tag, world_skill_system_rule_out_come = (
            gameplay_systems.skill_system_utils.parse_skill_world_harmony_inspector_action(
                entity
            )
        )

        logger.debug(f"world_skill_system_rule_tag: {world_skill_system_rule_tag}")

        self._context.notify_event(
            set({entity}),
            AgentEvent(
                message=_generate_offline_prompt(
                    self._context.safe_get_entity_name(entity),
                    self._context.safe_get_entity_name(target),
                    world_skill_system_rule_out_come,
                )
            ),
        )

    ######################################################################################################################################################
    def _generate_skill_impact_response_task(
        self, entity: Entity, target: Entity
    ) -> Optional[AgentTask]:

        target_agent_name = self._context.safe_get_entity_name(target)
        target_agent = self._context.agent_system.get_agent(target_agent_name)
        if target_agent is None:
            return None

        inspector_tag, inspector_content = (
            gameplay_systems.skill_system_utils.parse_skill_world_harmony_inspector_action(
                entity
            )
        )
        prompt = _generate_skill_impact_response_prompt(
            self._context.safe_get_entity_name(entity),
            target_agent_name,
            inspector_content,
            inspector_tag,
        )

        return AgentTask.create(
            target_agent,
            builtin_prompt_util.replace_you(prompt, target_agent_name),
        )

    ######################################################################################################################################################
    def _determine_damage_bonus(self, entity: Entity) -> float:

        inspector_tag, inspector_content = (
            gameplay_systems.skill_system_utils.parse_skill_world_harmony_inspector_action(
                entity
            )
        )

        if inspector_tag == builtin_prompt_util.ConstantSkillPrompt.CRITICAL_SUCCESS:
            return 1.5  # 先写死，测试的时候再改。todo

        return 1.0  # 默认的。

    ######################################################################################################################################################