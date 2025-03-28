from entitas import ExecuteProcessor, Matcher, Entity  # type: ignore
from pydantic import BaseModel
from extended_systems.chat_request_handler import ChatRequestHandler
from components.components_v_0_0_1 import (
    StageEnvironmentComponent,
    StagePermitComponent,
)
from overrides import override
from typing import Dict, List, Set, final
from game.tcg_game import TCGGame
from loguru import logger
import format_string.json_format


#######################################################################################################################################
@final
class StagePlanningResponse(BaseModel):
    environment_narration: str = ""


#######################################################################################################################################
def _generate_stage_plan_prompt(
    actors_appearances_mapping: Dict[str, str],
) -> str:

    actors_appearances_info = []
    for actor_name, appearance in actors_appearances_mapping.items():
        actors_appearances_info.append(f"{actor_name}: {appearance}")
    if len(actors_appearances_info) == 0:
        actors_appearances_info.append("无")

    stage_response_example = StagePlanningResponse(
        environment_narration="场景内的环境描述"
    )

    return f"""# 请你输出你的场景描述
## 场景内角色
{"\n".join(actors_appearances_info)}
## 输出内容-场景描述
- 场景内的环境描述，不要包含任何角色信息。
## 输出要求
- 所有输出必须为第三人称视角。
- 不要使用```json```来封装内容。
### 输出格式(JSON)
{stage_response_example.model_dump_json()}"""


#######################################################################################################################################
def _compress_stage_plan_prompt(prompt: str) -> str:
    return "# 请你输出你的场景描述。并以 JSON 格式输出。"


#######################################################################################################################################
@final
class StagePlanningSystem(ExecuteProcessor):

    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    #######################################################################################################################################
    @override
    def execute(self) -> None:
        pass

    #######################################################################################################################################
    @override
    async def a_execute1(self) -> None:
        await self._process_stage_planning_request()

    #######################################################################################################################################
    @override
    async def a_execute2(self) -> None:
        pass

    #######################################################################################################################################
    async def _process_stage_planning_request(self) -> None:

        stage_entities = self._game.get_group(
            Matcher(
                all_of=[
                    StagePermitComponent,
                ]
            )
        ).entities

        request_handlers: List[ChatRequestHandler] = (
            self._generate_chat_request_handlers(stage_entities)
        )

        await self._game.langserve_system.gather(request_handlers=request_handlers)

        self._handle_chat_responses(request_handlers)

    #######################################################################################################################################
    def _generate_chat_request_handlers(
        self, stage_entities: Set[Entity]
    ) -> List[ChatRequestHandler]:
        request_handlers: List[ChatRequestHandler] = []
        for entity in stage_entities:

            # 获取场景内角色的外貌信息
            actors_appearances_mapping: Dict[str, str] = (
                self._game.retrieve_actor_appearance_on_stage_mapping(entity)
            )

            # 生成提示信息
            message = _generate_stage_plan_prompt(actors_appearances_mapping)

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
    def _handle_chat_responses(
        self, request_handlers: List[ChatRequestHandler]
    ) -> None:
        for request_handler in request_handlers:

            if request_handler.response_content == "":
                continue

            entity2 = self._game.get_entity_by_name(request_handler._name)
            assert entity2 is not None

            self._handle_stage_response(entity2, request_handler)

    #######################################################################################################################################
    def _handle_stage_response(
        self, entity2: Entity, request_handler: ChatRequestHandler
    ) -> None:

        # 核心处理
        try:

            format_response = StagePlanningResponse.model_validate_json(
                format_string.json_format.strip_json_code_block(
                    request_handler.response_content
                )
            )

            # logger.warning(
            #     f"Stage: {entity2._name}, Response:\n{format_response.model_dump_json()}"
            # )

            self._game.append_human_message(
                entity2, _compress_stage_plan_prompt(request_handler._prompt)
            )
            self._game.append_ai_message(entity2, request_handler.response_content)

            # 更新环境描写
            if format_response.environment_narration != "":
                entity2.replace(
                    StageEnvironmentComponent,
                    entity2._name,
                    format_response.environment_narration,
                )

        except Exception as e:
            logger.error(f"Exception: {e}")


#######################################################################################################################################
