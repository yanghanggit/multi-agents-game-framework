from entitas import InitializeProcessor, ExecuteProcessor, Matcher, Entity  # type: ignore
from overrides import override
from game.rpg_game_context import RPGGameContext
from components.components import (
    PlanningFlagComponent,
    StageComponent,
    ActorComponent,
    EnterStageFlagComponent,
)
from game.rpg_game import RPGGame
from typing import List, Dict, Optional, final
from queue import Queue


@final
class ActorPlanningStrategySystem(InitializeProcessor, ExecuteProcessor):

    @override
    def __init__(self, context: RPGGameContext, rpg_game: RPGGame) -> None:
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game
        self._order_queues: Dict[str, Queue[str]] = {}

    ############################################################################################################
    @override
    def initialize(self) -> None:

        self._order_queues.clear()
        stage_entities = self._context.get_group(Matcher(StageComponent)).entities
        for stage_entity in stage_entities:
            self._extend_order_queue(self._order_queues, stage_entity, [])

    ############################################################################################################
    @override
    def execute(self) -> None:
        # 如果有最近的转换，就处理
        self._handle_recent_stage_transition_actors()
        # 添加自动规划组件
        self._handle_add_planning_component()
        # 删除
        self._handle_remove_enter_stage_component()

    ############################################################################################################
    def _handle_recent_stage_transition_actors(self) -> None:
        recent_stage_transition_actors: Dict[str, List[str]] = (
            self._analyze_recent_stage_transition_actors()
        )
        if len(recent_stage_transition_actors) == 0:
            return

        stage_entities = self._context.get_group(Matcher(StageComponent)).entities
        for stage_entity in stage_entities:

            stage_comp = stage_entity.get(StageComponent)
            self._extend_order_queue(
                self._order_queues,
                stage_entity,
                recent_stage_transition_actors.get(stage_comp.name, []),
            )

    ############################################################################################################
    def _handle_add_planning_component(self) -> None:
        stage_entities = self._context.get_group(
            Matcher(StageComponent, PlanningFlagComponent)
        ).entities

        for stage_entity in stage_entities:

            pop_actor_entity = self._pop_first_executable_actor_from_order_queue(
                self._order_queues, stage_entity
            )
            if pop_actor_entity is None:
                # try to fill again
                self._extend_order_queue(self._order_queues, stage_entity, [])
                pop_actor_entity = self._pop_first_executable_actor_from_order_queue(
                    self._order_queues, stage_entity
                )

            if pop_actor_entity is None:
                continue

            assert pop_actor_entity.has(ActorComponent)

            actor_comp = pop_actor_entity.get(ActorComponent)
            pop_actor_entity.replace(PlanningFlagComponent, actor_comp.name)

    ############################################################################################################
    def _extend_order_queue(
        self,
        order_queue: Dict[str, Queue[str]],
        stage_entity: Entity,
        append_recent_stage_transition_actors: List[str],
    ) -> None:

        stage_name = stage_entity.get(StageComponent).name
        actor_names = self._context.retrieve_actor_names_on_stage(stage_entity)

        # step1: 移除新进入场景的
        if len(append_recent_stage_transition_actors) > 0:
            actor_names = actor_names - set(append_recent_stage_transition_actors)

        # step2: 重建一组新的
        dq = order_queue.setdefault(stage_name, Queue[str]())
        for actor_name in actor_names:
            dq.put(actor_name)

        # step3: 新进入场景的加入到队列尾部
        for actor_name in append_recent_stage_transition_actors:
            dq.put(actor_name)

    ############################################################################################################
    def _analyze_recent_stage_transition_actors(self) -> Dict[str, List[str]]:
        ret: Dict[str, List[str]] = {}

        actor_entities = self._context.get_group(
            Matcher(EnterStageFlagComponent)
        ).entities

        for actor_entity in actor_entities:
            enter_stage_comp = actor_entity.get(EnterStageFlagComponent)
            ret.setdefault(enter_stage_comp.enter_stage, []).append(
                enter_stage_comp.name
            )

        return ret

    ############################################################################################################
    def _handle_remove_enter_stage_component(self) -> None:
        actor_entities = self._context.get_group(
            Matcher(EnterStageFlagComponent)
        ).entities.copy()
        for actor_entity in actor_entities:
            actor_entity.remove(EnterStageFlagComponent)

    ############################################################################################################
    def _pop_first_executable_actor_from_order_queue(
        self, order_queue: Dict[str, Queue[str]], stage_entity: Entity
    ) -> Optional[Entity]:

        stage_name = stage_entity.get(StageComponent).name
        order_queue_list = order_queue.setdefault(stage_name, Queue[str]())
        while not order_queue_list.empty():
            actor_name = order_queue_list.get()
            actor_entity = self._context.get_actor_entity(actor_name)
            if actor_entity is None:
                # 不存在的
                continue

            actor_comp = actor_entity.get(ActorComponent)
            if actor_comp.current_stage != stage_name:
                # 可能已经离开了。
                continue

            return actor_entity

        return None

    ############################################################################################################
