from entitas import Entity, Matcher, ExecuteProcessor  # type: ignore
from overrides import override
from components.components import (
    WorldSystemComponent,
    StageComponent,
    ActorComponent,
    FinalAppearanceComponent,
    KickOffContentComponent,
    KickOffFlagComponent,
    AgentPingFlagComponent,
)
from game.rpg_game_context import RPGGameContext
from typing import Dict, Set, final
from agent.agent_request_handler import AgentRequestHandler
from game.rpg_game import RPGGame
from components.actions import (
    MindVoiceAction,
    TagAction,
    StageNarrationAction,
    UpdateAppearanceAction,
    KickOffAction,
)
from components.actions import UpdateAppearanceAction
import gameplay_systems.prompt_utils
from agent.agent_response_handler import AgentResponseHandler
import gameplay_systems.stage_entity_utils
import gameplay_systems.task_request_utils


###############################################################################################################################################
def _generate_actor_kick_off_prompt(kick_off_message: str, epoch_script: str) -> str:
    return f"""# 游戏启动!
见‘游戏流程’-‘游戏启动’，游戏系统将提供初始设定，包括角色、场景、道具信息，以及剧情开端。
你将开始你的扮演，此时的世界背景如下，请仔细阅读并牢记，以确保你的行为和言语符合游戏设定，不会偏离时代背景。

## 当前世界背景
{epoch_script}

## 你的初始设定
{kick_off_message}

## 输出要求
- 生成的内容应符合当前世界背景。
- 请遵循 输出格式指南。
- 返回结果 只 包含:{MindVoiceAction.__name__}与{TagAction.__name__}。"""


###############################################################################################################################################
def _generate_stage_kick_off_prompt(
    kick_off_message: str,
    input_actors_on_stage: Set[str],
    epoch_script: str,
) -> str:

    actors_on_stage_prompt = list(input_actors_on_stage)
    if len(actors_on_stage_prompt) == 0:
        actors_on_stage_prompt.append("无")

    return f"""# 游戏启动!
见‘游戏流程’-‘游戏启动’，游戏系统将提供初始设定，包括角色、场景、道具信息，以及剧情开端。
你将开始你的扮演，此时的世界背景如下，请仔细阅读并牢记，以确保你的行为和言语符合游戏设定，不会偏离时代背景。

## 当前世界背景
{epoch_script}

## 场景内的角色
{"\n".join(actors_on_stage_prompt)}

## 你的初始设定
{kick_off_message}

{gameplay_systems.prompt_utils.generate_stage_narration_prompt()}

## 输出要求
- 生成的内容应符合当前世界背景。
- 请遵循 输出格式指南。
- 返回结果 只 包含:{StageNarrationAction.__name__} 和 {TagAction.__name__}。"""


###############################################################################################################################################
def _generate_world_system_kick_off_prompt(epoch_script: str) -> str:
    return f"""# 游戏启动! 请回答你的职能与描述"""


######################################################################################################################################################
@final
class AgentKickOffSystem(ExecuteProcessor):
    def __init__(self, context: RPGGameContext, rpg_game: RPGGame) -> None:
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game

    ######################################################################################################################################################
    def _initialize_tasks(self) -> Dict[str, AgentRequestHandler]:

        ret: Dict[str, AgentRequestHandler] = {}

        world_tasks = self._initialize_world_system_tasks()
        stage_tasks = self._initialize_stage_tasks()
        actor_tasks = self._initialize_actor_tasks()

        ret.update(world_tasks)
        ret.update(stage_tasks)
        ret.update(actor_tasks)

        return ret

    ######################################################################################################################################################
    @override
    def execute(self) -> None:
        pass

    ######################################################################################################################################################
    @override
    async def a_execute1(self) -> None:

        # 处理kick off任务
        await self._process_kick_off_tasks()

        # 初始化更新外观的action
        self._initialize_appearance_update_action()

    ######################################################################################################################################################
    async def _process_kick_off_tasks(self) -> None:
        agent_tasks: Dict[str, AgentRequestHandler] = self._initialize_tasks()
        if len(agent_tasks) == 0:
            return

        # 执行全部的任务
        await gameplay_systems.task_request_utils.gather(
            [task for task in agent_tasks.values()]
        )

        # 处理结果
        self._process_agent_tasks(agent_tasks)

        # 记录场景叙述
        self._process_stage_narrate_action(agent_tasks)

    ######################################################################################################################################################
    def _initialize_world_system_tasks(self) -> Dict[str, AgentRequestHandler]:

        ret: Dict[str, AgentRequestHandler] = {}

        world_entities: Set[Entity] = self._context.get_group(
            Matcher(
                all_of=[
                    WorldSystemComponent,
                    KickOffContentComponent,
                    AgentPingFlagComponent,
                ],
                none_of=[KickOffFlagComponent],
            )
        ).entities
        for world_entity in world_entities:
            agent = self._context.safe_get_agent(world_entity)
            assert (
                len(agent._chat_history) == 0
            ), f"chat_history is not empty, {agent._chat_history}"

            ret[agent.name] = AgentRequestHandler.create_with_full_context(
                agent,
                _generate_world_system_kick_off_prompt(epoch_script=""),
            )

        return ret

    ######################################################################################################################################################
    def _initialize_stage_tasks(self) -> Dict[str, AgentRequestHandler]:

        ret: Dict[str, AgentRequestHandler] = {}

        stage_entities: Set[Entity] = self._context.get_group(
            Matcher(
                all_of=[
                    StageComponent,
                    KickOffContentComponent,
                    AgentPingFlagComponent,
                ],
                none_of=[KickOffFlagComponent],
            )
        ).entities
        for stage_entity in stage_entities:
            agent = self._context.safe_get_agent(stage_entity)
            assert (
                len(agent._chat_history) == 0
            ), f"chat_history is not empty, {agent._chat_history}"

            kick_off_comp = stage_entity.get(KickOffContentComponent)
            kick_off_prompt = _generate_stage_kick_off_prompt(
                kick_off_message=kick_off_comp.content,
                input_actors_on_stage=self._context.retrieve_actor_names_on_stage(
                    stage_entity
                ),
                epoch_script=self._game.epoch_script,
            )
            ret[agent.name] = AgentRequestHandler.create_with_full_context(
                agent, kick_off_prompt
            )

        return ret

    ######################################################################################################################################################
    def _initialize_actor_tasks(self) -> Dict[str, AgentRequestHandler]:

        ret: Dict[str, AgentRequestHandler] = {}

        actor_entities: Set[Entity] = self._context.get_group(
            Matcher(
                all_of=[
                    ActorComponent,
                    KickOffContentComponent,
                    AgentPingFlagComponent,
                ],
                none_of=[KickOffFlagComponent],
            )
        ).entities
        for actor_entity in actor_entities:
            agent = self._context.safe_get_agent(actor_entity)
            assert (
                len(agent._chat_history) == 0
            ), f"chat_history is not empty, {agent._chat_history}"

            kick_off_comp = actor_entity.get(KickOffContentComponent)
            ret[agent.name] = AgentRequestHandler.create_with_full_context(
                agent,
                _generate_actor_kick_off_prompt(
                    kick_off_message=kick_off_comp.content,
                    epoch_script=self._game.epoch_script,
                ),
            )

        return ret

    ######################################################################################################################################################
    def _process_agent_tasks(self, tasks: Dict[str, AgentRequestHandler]) -> None:
        for agent_name, _ in tasks.items():
            entity = self._context.get_entity_by_name(agent_name)
            assert entity is not None, f"entity is None, {agent_name}"
            if entity is None:
                continue
            entity.replace(KickOffFlagComponent, agent_name)
            entity.replace(
                KickOffAction,
                agent_name,
                [],
            )

    ######################################################################################################################################################
    def _process_stage_narrate_action(
        self, tasks: Dict[str, AgentRequestHandler]
    ) -> None:
        for agent_name, agent_task in tasks.items():
            entity = self._context.get_entity_by_name(agent_name)
            assert entity is not None, f"entity is None, {agent_name}"
            if entity is None or not entity.has(StageComponent):
                continue

            gameplay_systems.stage_entity_utils.apply_stage_narration(
                self._context,
                AgentResponseHandler(agent_name, agent_task.response_content),
            )

    ######################################################################################################################################################
    def _initialize_appearance_update_action(self) -> None:

        actor_entities = self._context.get_group(
            Matcher(FinalAppearanceComponent)
        ).entities
        for actor_entity in actor_entities:

            appearance_comp = actor_entity.get(FinalAppearanceComponent)
            if appearance_comp.final_appearance == "":
                actor_entity.replace(
                    UpdateAppearanceAction,
                    appearance_comp.name,
                    [],
                )

    ######################################################################################################################################################
