from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from overrides import override
from ecs_systems.action_components import SpeakAction, BroadcastAction, WhisperAction
from ecs_systems.components import PlayerComponent, ActorComponent
from rpg_game.rpg_entitas_context import RPGEntitasContext
from ecs_systems.stage_director_component import StageDirectorComponent
from typing import List, Set, Dict
import ecs_systems.cn_builtin_prompt as builtin_prompt
from my_agent.lang_serve_agent_request_task import (
    LangServeAgentRequestTask,
    LangServeAgentAsyncRequestTasksGather,
)


# 这个类就是故意打包将对话类事件先进行一次request，如果LLM发现有政策问题就会抛异常，不会将污染的message加入chat history，这样就不可能进入chat_history。
# 这么做是防止玩家的对话内容包含了非法信息和违反政策的内容。
#################################################################################################################################################
class PostConversationActionSystem(ReactiveProcessor):
    def __init__(self, context: RPGEntitasContext) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context
        self._async_execute: bool = True
        self._tasks: Dict[str, LangServeAgentRequestTask] = {}

    #################################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {
            Matcher(
                any_of=[SpeakAction, BroadcastAction, WhisperAction]
            ): GroupEvent.ADDED
        }

    #################################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        # 如果去掉entity.has(PlayerComponent)。就是处理所有的Actor的对话事件，最保险的做法。
        # 有PlayerComponent就节省一些
        return entity.has(PlayerComponent) and entity.has(ActorComponent)

    #################################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:

        ## 所有场景，发生了任何对话的事件
        stage_entities: Set[Entity] = set()
        for entity in entities:
            stage_entity = self._context.safe_get_stage_entity(entity)
            if stage_entity is not None:
                stage_entities.add(stage_entity)

        self._tasks.clear()
        for stage_entity in stage_entities:
            self.before(stage_entity)
            self.handle(stage_entity, self._async_execute, self._tasks)
            self.after(stage_entity)

    #################################################################################################################################################
    def before(self, stage_entity: Entity) -> None:
        pass

    #################################################################################################################################################
    def after(self, stage_entity: Entity) -> None:
        assert stage_entity.has(StageDirectorComponent)
        stage_entity.get(StageDirectorComponent).clear()

    #################################################################################################################################################
    def handle(
        self,
        stage_entity: Entity,
        async_execute: bool,
        request_tasks: Dict[str, LangServeAgentRequestTask],
    ) -> None:

        stage_director_comp: StageDirectorComponent = stage_entity.get(
            StageDirectorComponent
        )
        if len(stage_director_comp._director_events) == 0:
            return
        ##
        # 处理场景的
        raw_events2stage = stage_director_comp.to_stage(
            stage_director_comp.name, self._context
        )
        if len(raw_events2stage) > 0:
            batch_events2stage_prompt = self.batch_stage_events(
                stage_director_comp.name, raw_events2stage
            )
            if async_execute:
                agent = self._context._langserve_agent_system.get_agent(
                    stage_director_comp.name
                )
                if agent is not None:
                    task = LangServeAgentRequestTask.create_for_checking_prompt(
                        agent, batch_events2stage_prompt
                    )
                    if task is not None:
                        request_tasks[stage_director_comp.name] = task
            else:
                self.imme_request(stage_director_comp.name, batch_events2stage_prompt)

        ### 处理Actor的
        actors_in_this_stage = self._context.actors_in_stage(stage_director_comp.name)
        for actor_entity in actors_in_this_stage:

            actor_comp = actor_entity.get(ActorComponent)
            raw_events2actor = stage_director_comp.to_actor(
                actor_comp.name, self._context
            )

            if len(raw_events2actor) == 0:
                continue

            batch_events2actor_prompt = self.batch_actor_events(
                stage_director_comp.name, raw_events2actor
            )

            if actor_entity.has(PlayerComponent):
                self._context.safe_add_human_message_to_entity(
                    actor_entity, batch_events2actor_prompt
                )
                continue

            if async_execute:
                agent = self._context._langserve_agent_system.get_agent(actor_comp.name)
                if agent is not None:
                    task = LangServeAgentRequestTask.create_for_checking_prompt(
                        agent, batch_events2stage_prompt
                    )
                    if task is not None:
                        request_tasks[actor_comp.name] = task
            else:
                self.imme_request(actor_comp.name, batch_events2actor_prompt)

    #################################################################################################################################################
    def imme_request(self, name: str, prompt: str) -> None:

        agent = self._context._langserve_agent_system.get_agent(name)
        if agent is None:
            return

        task = LangServeAgentRequestTask.create_for_checking_prompt(agent, prompt)
        if task is None:
            return

        task.request()

    #################################################################################################################################################
    def batch_stage_events(self, stagename: str, events2stage: List[str]) -> str:
        return builtin_prompt.batch_conversation_action_events_in_stage_prompt(
            stagename, events2stage
        )

    #################################################################################################################################################
    def batch_actor_events(self, stagename: str, events2actor: List[str]) -> str:
        return builtin_prompt.batch_conversation_action_events_in_stage_prompt(
            stagename, events2actor
        )

    #################################################################################################################################################
    async def async_post_execute(self) -> None:
        if len(self._tasks) == 0:
            return
        gather = LangServeAgentAsyncRequestTasksGather(
            "PostConversationActionSystem", self._tasks
        )
        await gather.gather()
        self._tasks.clear()


#################################################################################################################################################
