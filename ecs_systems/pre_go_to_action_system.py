from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from ecs_systems.action_components import (
    GoToAction,
    TagAction,
    DeadAction,
    WhisperAction,
)
from ecs_systems.components import (
    StageComponent,
    ActorComponent,
    AppearanceComponent,
)
from rpg_game.rpg_entitas_context import RPGEntitasContext
from loguru import logger
from ecs_systems.stage_director_component import StageDirectorComponent
from ecs_systems.stage_director_event import IStageDirectorEvent
import ecs_systems.cn_builtin_prompt as builtin_prompt
from ecs_systems.cn_constant_prompt import _CNConstantPrompt_
from typing import cast, override, List
from ecs_systems.check_status_action_system import CheckStatusActionHelper
from my_agent.agent_plan import AgentPlan, AgentAction
from my_agent.lang_serve_agent_request_task import LangServeAgentRequestTask
from file_system.files_def import PropFile


####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class ActorGoToFailedBecauseStageInvalid(IStageDirectorEvent):

    def __init__(self, actor_name: str, stage_name: str) -> None:
        self._actor_name: str = actor_name
        self._stage_name: str = stage_name

    def to_actor(self, actor_name: str, extended_context: RPGEntitasContext) -> str:
        if actor_name != self._actor_name:
            # 跟你无关不用关注，原因类的东西，是失败后矫正用，所以只有自己知道即可
            return ""
        return builtin_prompt.go_to_stage_failed_because_stage_is_invalid_prompt(
            self._actor_name, self._stage_name
        )

    def to_stage(self, stage_name: str, extended_context: RPGEntitasContext) -> str:
        return ""


####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class ActorGoToFailedBecauseAlreadyInStage(IStageDirectorEvent):

    def __init__(self, actor_name: str, stage_name: str) -> None:
        self._actor_name: str = actor_name
        self._stage_name: str = stage_name

    def to_actor(self, actor_name: str, extended_context: RPGEntitasContext) -> str:
        if actor_name != self._actor_name:
            # 跟你无关不用关注，原因类的东西，是失败后矫正用，所以只有自己知道即可
            return ""
        return builtin_prompt.go_to_stage_failed_because_already_in_stage_prompt(
            self._actor_name, self._stage_name
        )

    def to_stage(self, stage_name: str, extended_context: RPGEntitasContext) -> str:
        return ""


####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class ActorExitStageFailedBecauseStageRefuse(IStageDirectorEvent):
    def __init__(self, actor_name: str, stage_name: str, tips: str) -> None:
        self._actor_name: str = actor_name
        self._stage_name: str = stage_name
        self._tips: str = tips

    def to_actor(self, actor_name: str, extended_context: RPGEntitasContext) -> str:
        if actor_name != self._actor_name:
            return ""
        return builtin_prompt.exit_stage_failed_beacuse_stage_refuse_prompt(
            self._actor_name, self._stage_name, self._tips
        )

    def to_stage(self, stage_name: str, extended_context: RPGEntitasContext) -> str:
        return ""


####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class ActorEnterStageFailedBecauseStageRefuse(IStageDirectorEvent):
    def __init__(self, actor_name: str, stage_name: str, tips: str) -> None:
        self._actor_name: str = actor_name
        self._stage_name: str = stage_name
        self._tips: str = tips

    def to_actor(self, actor_name: str, extended_context: RPGEntitasContext) -> str:
        if actor_name != self._actor_name:
            return ""
        return builtin_prompt.enter_stage_failed_beacuse_stage_refuse_prompt(
            self._actor_name, self._stage_name, self._tips
        )

    def to_stage(self, stage_name: str, extended_context: RPGEntitasContext) -> str:
        return ""


class StageConditionsCheckPlan(AgentPlan):

    def __init__(self, name: str, raw_data: str) -> None:
        super().__init__(name, raw_data)

    @property
    def allow(self) -> bool:
        tip_action = self.get_action_by_key(TagAction.__name__)
        if tip_action is None or len(tip_action.values) == 0:
            return False
        first_value = tip_action.values[0].lower()
        return first_value == "yes" or first_value == "true"

    @property
    def show_tips(self) -> str:
        whisper_action = self.get_action_by_key(WhisperAction.__name__)
        if whisper_action is None or len(whisper_action.values) == 0:
            return ""
        return " ".join(whisper_action.values)


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
class PreBeforeGoToActionSystem(ReactiveProcessor):

    def __init__(self, context: RPGEntitasContext) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context

    ###############################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(GoToAction): GroupEvent.ADDED}

    ###############################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return (
            entity.has(GoToAction)
            and entity.has(ActorComponent)
            and not entity.has(DeadAction)
        )

    ###############################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:

        for entity in entities:

            # f"未知场景({guid})"
            self.trans_guid_stage_name(entity)

            # 检查目标场景是否有效，可能是无效的，例如不存在，或者已经在目标场景了
            if not self.base_check(entity):
                self.on_failed(entity)
                continue

            # 检查离开当前场景的条件是否满足，需要LLM推理
            exit_result = self.handle_exit_stage_with_conditions(entity)
            if not exit_result:
                self.on_failed(entity)
                continue

            # 检查进入目标场景的条件是否满足，需要LLM推理
            enter_result = self.handle_enter_stage_with_conditions(entity)
            if not enter_result:
                self.on_failed(entity)
                continue

            # 通过了，可以去下一个场景了
            logger.debug(
                f"{self._context.safe_get_entity_name(entity)} 通过了离开和进入条件，可以去下一个场景了"
            )

    ###############################################################################################################################################
    def base_check(self, actor_entity: Entity) -> bool:

        safe_actor_name = self._context.safe_get_entity_name(actor_entity)
        current_stage_entity = self._context.safe_get_stage_entity(actor_entity)
        if current_stage_entity is None:
            logger.error(f"{safe_actor_name}没有当前场景，这是个错误")
            return False

        target_stage_name = self.get_target_stage_name(actor_entity)
        target_stage_entity = self._context.get_stage_entity(
            self.get_target_stage_name(actor_entity)
        )
        if target_stage_entity is None:
            # 无效的去往目标!
            StageDirectorComponent.add_event_to_stage_director(
                self._context,
                current_stage_entity,
                ActorGoToFailedBecauseStageInvalid(safe_actor_name, target_stage_name),
            )
            return False

        if current_stage_entity == target_stage_entity:
            # 已经在这个场景里了，不要重复去了
            StageDirectorComponent.add_event_to_stage_director(
                self._context,
                current_stage_entity,
                ActorGoToFailedBecauseAlreadyInStage(
                    safe_actor_name, target_stage_name
                ),
            )
            return False

        return True

    ###############################################################################################################################################
    def has_exit_conditions(self, stage_entity: Entity) -> bool:

        safe_name = self._context.safe_get_entity_name(stage_entity)
        kickoff = self._context._kick_off_message_system.get_message(safe_name)
        return _CNConstantPrompt_.STAGE_EXIT_TAG in kickoff

        # return (
        #     stage_entity.has(StageExitCondStatusComponent)
        #     or stage_entity.has(StageExitCondCheckActorStatusComponent)
        #     or stage_entity.has(StageExitCondCheckActorPropsComponent)
        # )

    ###############################################################################################################################################
    def has_entry_conditions(self, stage_entity: Entity) -> bool:
        safe_name = self._context.safe_get_entity_name(stage_entity)
        kickoff = self._context._kick_off_message_system.get_message(safe_name)
        return _CNConstantPrompt_.STAGE_ENTRY_TAG in kickoff
        # return (
        #     stage_entity.has(StageEntryCondStatusComponent)
        #     or stage_entity.has(StageEntryCondCheckActorStatusComponent)
        #     or stage_entity.has(StageEntryCondCheckActorPropsComponent)
        # )

    ###############################################################################################################################################
    def handle_exit_stage_with_conditions(self, actor_entity: Entity) -> bool:
        #
        current_stage_entity = self._context.safe_get_stage_entity(actor_entity)
        assert current_stage_entity is not None
        if not self.has_exit_conditions(current_stage_entity):
            return True
        #
        actor_name = self._context.safe_get_entity_name(actor_entity)
        current_stage_name = self._context.safe_get_entity_name(current_stage_entity)

        final_prompt = builtin_prompt.stage_exit_conditions_check_prompt(
            actor_name,
            current_stage_name,
            self.get_actor_status_prompt(actor_entity),
            self.get_actor_props(actor_entity),
        )

        ## 让大模型去推断是否可以离开，分别检查stage自身，角色状态（例如长相），角色道具（拥有哪些道具与文件）
        agent = self._context._langserve_agent_system.get_agent(current_stage_name)
        if agent is None:
            return False

        task = LangServeAgentRequestTask.create(agent, final_prompt)
        if task is None:
            return False

        response = task.request()
        if response is None:
            return False

        plan = StageConditionsCheckPlan(
            current_stage_name, response
        )  # AgentPlan(current_stage_name, response)
        # handle_response_helper = HandleStageConditionsResponseHelper(plan)
        # if not handle_response_helper.parse():
        #     return False

        #
        if not plan.allow:
            # 通知事件
            StageDirectorComponent.add_event_to_stage_director(
                self._context,
                current_stage_entity,
                ActorExitStageFailedBecauseStageRefuse(
                    actor_name, current_stage_name, plan.show_tips
                ),
            )
            return False

        logger.debug(f"允许通过！说明如下: {plan.show_tips}")
        ## 可以删除，允许通过！这个上下文就拿掉，不需要了。
        self._context._langserve_agent_system.remove_last_conversation_between_human_and_ai(
            current_stage_name
        )
        return True

    ###############################################################################################################################################
    def handle_enter_stage_with_conditions(self, actor_entity: Entity) -> bool:

        target_stage_entity = self._context.get_stage_entity(
            self.get_target_stage_name(actor_entity)
        )
        assert target_stage_entity is not None
        if target_stage_entity is None:
            return False

        ##
        if not self.has_entry_conditions(target_stage_entity):
            return True

        ##
        actor_name = self._context.safe_get_entity_name(actor_entity)
        target_stage_name = self._context.safe_get_entity_name(target_stage_entity)

        # 最终提示词
        final_prompt = builtin_prompt.stage_entry_conditions_check_prompt(
            actor_name,
            target_stage_name,
            self.get_actor_status_prompt(actor_entity),
            self.get_actor_props(actor_entity),
        )

        ## 让大模型去推断是否可以离开，分别检查stage自身，角色状态（例如长相），角色道具（拥有哪些道具与文件）
        agent = self._context._langserve_agent_system.get_agent(target_stage_name)
        if agent is None:
            return False

        task = LangServeAgentRequestTask.create(agent, final_prompt)
        if task is None:
            return False

        response = task.request()
        if response is None:
            return False

        plan = StageConditionsCheckPlan(
            target_stage_name, response
        )  # AgentPlan(target_stage_name, response)
        # handle_response_helper = HandleStageConditionsResponseHelper(plan)
        # if not handle_response_helper.parse():
        #     return False

        if not plan.allow:
            # 通知事件, 因为没动，得是当前场景需要通知
            current_stage_entity = self._context.safe_get_stage_entity(actor_entity)
            assert current_stage_entity is not None
            StageDirectorComponent.add_event_to_stage_director(
                self._context,
                current_stage_entity,
                ActorEnterStageFailedBecauseStageRefuse(
                    actor_name, target_stage_name, plan.show_tips
                ),
            )
            return False

        logger.debug(f"允许通过！说明如下: {plan.show_tips}")
        ## 可以删除，允许通过！这个上下文就拿掉，不需要了。
        self._context._langserve_agent_system.remove_last_conversation_between_human_and_ai(
            target_stage_name
        )
        return True

    ###############################################################################################################################################
    def get_target_stage_name(self, actor_entity: Entity) -> str:
        assert actor_entity.has(ActorComponent)
        assert actor_entity.has(GoToAction)

        go_to_action = actor_entity.get(GoToAction)
        if len(go_to_action.values) == 0:
            return ""
        return str(go_to_action.values[0])

    ###############################################################################################################################################
    def get_actor_status_prompt(self, actor_entity: Entity) -> str:
        assert actor_entity.has(ActorComponent)
        if not actor_entity.has(AppearanceComponent):
            return ""

        appearance_comp = actor_entity.get(AppearanceComponent)
        return builtin_prompt.actor_status_when_stage_change_prompt(
            appearance_comp.name, cast(str, appearance_comp.appearance)
        )

    ###############################################################################################################################################
    def get_actor_props(self, actor_entity: Entity) -> List[PropFile]:
        helper = CheckStatusActionHelper(self._context)
        helper.check_status(actor_entity)
        return (
            helper._prop_files_as_weapon_clothes_non_consumable_item
            + helper._prop_files_as_special_components
        )

    ###############################################################################################################################################
    def on_failed(self, actor_entity: Entity) -> None:
        if actor_entity.has(GoToAction):
            actor_entity.remove(GoToAction)

    ###############################################################################################################################################
    def trans_guid_stage_name(self, actor_entity: Entity) -> None:
        assert actor_entity.has(ActorComponent)
        assert actor_entity.has(GoToAction)

        go_to_action = actor_entity.get(GoToAction)
        if len(go_to_action.values) == 0:
            return
        check_unknown_guid_stage_name = go_to_action.values[0]
        if not builtin_prompt.is_unknown_guid_stage_name_prompt(
            check_unknown_guid_stage_name
        ):
            return

        logger.debug(f"current_name = {check_unknown_guid_stage_name}")
        guid = builtin_prompt.extract_from_unknown_guid_stage_name_prompt(
            check_unknown_guid_stage_name
        )
        stage_entity = self._context.get_entity_by_guid(guid)
        if stage_entity is None:
            logger.error(f"未知的场景GUID({guid})")
            return

        if not stage_entity.has(StageComponent):
            logger.error(f"({guid}) 对应的不是一个场景")
            return

        go_to_action.values[0] = self._context.safe_get_entity_name(stage_entity)


###############################################################################################################################################