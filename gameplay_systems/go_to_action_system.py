from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from gameplay_systems.action_components import GoToAction, DeadAction
from gameplay_systems.components import ActorComponent
from rpg_game.rpg_entitas_context import RPGEntitasContext
from typing import override, Optional
import gameplay_systems.cn_builtin_prompt as builtin_prompt
from rpg_game.rpg_game import RPGGame
from file_system.files_def import StageArchiveFile
from loguru import logger


###############################################################################################################################################
class GoToHelper:

    def __init__(
        self, context: RPGEntitasContext, entity: Entity, target_stage_name: str
    ) -> None:

        self._context: RPGEntitasContext = context
        self._entity: Entity = entity
        self._current_stage_name: str = entity.get(ActorComponent).current_stage
        self._current_stage_entity: Optional[Entity] = self._context.get_stage_entity(
            self._current_stage_name
        )
        assert self._current_stage_entity is not None
        self._target_stage_name: str = target_stage_name
        self._target_stage_entity: Optional[Entity] = self._context.get_stage_entity(
            target_stage_name
        )
        assert self._target_stage_entity is not None


class GoToActionSystem(ReactiveProcessor):

    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

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
            self.handle(entity)

    ###############################################################################################################################################
    def handle(self, entity: Entity) -> None:

        assert entity.has(GoToAction)
        go_to_action = entity.get(GoToAction)
        if len(go_to_action.values) == 0:
            return

        helper = GoToHelper(self._context, entity, go_to_action.values[0])
        if (
            helper._target_stage_entity is None
            or helper._current_stage_entity is None
            or helper._target_stage_entity == helper._current_stage_entity
        ):
            return

        if helper._current_stage_entity is not None:
            # 离开前的处理
            self.before_leave_current_stage(helper)
            # 离开
            self.leave_current_stage(helper)

        # 进入新的场景
        self.enter_target_stage(helper)

    ###############################################################################################################################################
    def enter_target_stage(self, helper: GoToHelper) -> None:

        actor_comp = helper._entity.get(ActorComponent)

        # 真正的进入场景
        helper._entity.replace(
            ActorComponent, actor_comp.name, helper._target_stage_name
        )

        # 更新场景标记
        self._context.change_stage_tag_component(
            helper._entity, helper._current_stage_name, helper._target_stage_name
        )

        assert helper._target_stage_entity is not None
        self._context.add_event_to_agents_in_stage(
            helper._target_stage_entity,
            builtin_prompt.make_enter_stage_prompt1(
                actor_comp.name, helper._target_stage_name
            ),
        )

        self._context.add_event_to_agent(
            set({helper._entity}),
            builtin_prompt.make_enter_stage_prompt2(
                actor_comp.name, helper._target_stage_name, helper._current_stage_name
            ),
        )

    ###############################################################################################################################################
    def before_leave_current_stage(self, helper: GoToHelper) -> None:

        my_name = self._context.safe_get_entity_name(helper._entity)
        stage_archive = self._context._file_system.get_file(
            StageArchiveFile, my_name, helper._current_stage_name
        )
        if stage_archive is None:
            return

        logger.debug(
            f"{my_name}离开{helper._current_stage_name}。留下最后的印象。{stage_archive._stage_narrate}"
        )
        self._context.add_event_to_agent(
            set({helper._entity}),
            builtin_prompt.make_last_impression_of_stage_prompt(
                my_name, helper._current_stage_name, stage_archive._stage_narrate
            ),
        )

    ###############################################################################################################################################
    def leave_current_stage(self, helper: GoToHelper) -> None:

        # 离开场景的事件需要通知相关的人
        assert helper._current_stage_entity is not None
        actor_comp = helper._entity.get(ActorComponent)
        self._context.add_event_to_agents_in_stage(
            helper._current_stage_entity,
            builtin_prompt.make_leave_stage_prompt(
                actor_comp.name, helper._current_stage_name, helper._target_stage_name
            ),
        )

        # 离开场景 设置成空
        helper._entity.replace(ActorComponent, actor_comp.name, "")

        # 更新场景标记
        self._context.change_stage_tag_component(
            helper._entity, helper._current_stage_name, ""
        )


###############################################################################################################################################
