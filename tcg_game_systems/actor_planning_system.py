from pydantic import BaseModel
from entitas import ExecuteProcessor, Matcher, Entity  # type: ignore
from extended_systems.chat_request_handler import ChatRequestHandler
import format_string.json_format
from components.components_v_0_0_1 import (
    StageEnvironmentComponent,
    ActorPermitComponent,
)
from overrides import override
from typing import Dict, List, final
from game.tcg_game import TCGGame
from loguru import logger
from components.actions_v_0_0_1 import (
    SpeakAction,
    MindVoiceAction,
    WhisperAction,
    AnnounceAction,
)


#######################################################################################################################################
@final
class ActorPlanningResponse(BaseModel):
    speak_actions: Dict[str, str] = {}
    whisper_actions: Dict[str, str] = {}
    announce_actions: str = ""
    mind_voice_actions: str = ""


#######################################################################################################################################
def _generate_actor_plan_prompt(
    current_stage: str,
    current_stage_narration: str,
    actors_appearance_mapping: Dict[str, str],
) -> str:

    actors_appearances_info = []
    for actor_name, appearance in actors_appearance_mapping.items():
        actors_appearances_info.append(f"{actor_name}: {appearance}")
    if len(actors_appearances_info) == 0:
        actors_appearances_info.append("无")

    # 格式示例
    actor_response_example = ActorPlanningResponse(
        speak_actions={
            "场景内角色全名": "你要说的内容（场景内其他角色会听见）",
        },
        whisper_actions={
            "场景内角色全名": "你要说的内容（只有你和目标角色能听见）",
        },
        announce_actions="你要说的内容（所有的角色都能听见）",
        mind_voice_actions="你要说的内容（内心独白，只有你自己能听见）",
    )

    return f"""# 请制定你的行动计划。
## 当前场景
{current_stage}
### 场景描述
{current_stage_narration}
## 场景内角色
{"\n".join(actors_appearances_info)}
## 输出要求
- 引用角色或场景时，请严格遵守全名机制
- 所有输出必须为第一人称视角。
### 输出格式规范
{actor_response_example.model_dump_json()}
- 注意！speak_actions/whisper_actions/announce_actions只能3选1，mind_voice_actions可选。
- 禁用换行/空行。
- 直接输出合规JSON。"""


#######################################################################################################################################
def _compress_actor_plan_prompt(
    prompt: str,
) -> str:
    return "# 请做出你的计划，决定你将要做什么，并以 JSON 格式输出。"


#######################################################################################################################################
@final
class ActorPlanningSystem(ExecuteProcessor):

    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    #######################################################################################################################################
    @override
    def execute(self) -> None:
        pass

    #######################################################################################################################################
    @override
    async def a_execute1(self) -> None:
        await self._process_actor_planning_request()

    #######################################################################################################################################
    async def _process_actor_planning_request(self) -> None:

        # 获取所有需要进行角色规划的角色
        actor_entities = self._game.get_group(
            Matcher(
                all_of=[
                    ActorPermitComponent,
                ],
            )
        ).entities

        # 处理角色规划请求
        request_handlers: List[ChatRequestHandler] = self._generate_chat_requests(
            actor_entities
        )

        # 语言服务
        await self._game.langserve_system.gather(request_handlers=request_handlers)

        # 处理角色规划请求
        self._handle_chat_responses(request_handlers)

    #######################################################################################################################################
    def _handle_chat_responses(
        self, request_handlers: List[ChatRequestHandler]
    ) -> None:

        for request_handler in request_handlers:

            if request_handler.response_content == "":
                continue

            entity2 = self._game.get_entity_by_name(request_handler._name)
            assert entity2 is not None
            self._handle_actor_response(entity2, request_handler)

    #######################################################################################################################################
    def _handle_actor_response(
        self, entity2: Entity, request_handler: ChatRequestHandler
    ) -> None:

        assert entity2.has(ActorPermitComponent)
        assert entity2._name == request_handler._name

        # 核心处理
        try:

            format_response = ActorPlanningResponse.model_validate_json(
                format_string.json_format.strip_json_code_block(
                    request_handler.response_content
                )
            )

            self._game.append_human_message(
                entity2, _compress_actor_plan_prompt(request_handler._prompt)
            )
            self._game.append_ai_message(entity2, request_handler.response_content)

            # 添加说话动作
            if len(format_response.speak_actions) > 0:
                entity2.replace(
                    SpeakAction, entity2._name, format_response.speak_actions
                )

            # 添加耳语动作
            if len(format_response.whisper_actions) > 0:
                entity2.replace(
                    WhisperAction, entity2._name, format_response.whisper_actions
                )

            # 添加宣布动作
            if format_response.announce_actions != "":
                entity2.replace(
                    AnnounceAction, entity2._name, format_response.announce_actions
                )

            # 添加内心独白
            if format_response.mind_voice_actions != "":
                entity2.replace(
                    MindVoiceAction, entity2._name, format_response.mind_voice_actions
                )

        except Exception as e:
            logger.error(f"Exception: {e}")

    #######################################################################################################################################
    def _generate_chat_requests(
        self, actor_entities: set[Entity]
    ) -> List[ChatRequestHandler]:

        request_handlers: List[ChatRequestHandler] = []

        for entity in actor_entities:

            current_stage = self._game.safe_get_stage_entity(entity)
            assert current_stage is not None

            # 找到当前场景内所有角色
            actors_apperances_mapping = (
                self._game.retrieve_actor_appearance_on_stage_mapping(current_stage)
            )
            actors_apperances_mapping.pop(entity._name, None)

            # 生成消息
            message = _generate_actor_plan_prompt(
                current_stage._name,
                current_stage.get(StageEnvironmentComponent).narrate,
                actors_apperances_mapping,
            )

            # 生成请求处理器
            request_handlers.append(
                ChatRequestHandler(
                    name=entity._name,
                    prompt=message,
                    chat_history=self._game.get_agent_short_term_memory(
                        entity
                    ).chat_history,
                )
            )

        return request_handlers

    #######################################################################################################################################
