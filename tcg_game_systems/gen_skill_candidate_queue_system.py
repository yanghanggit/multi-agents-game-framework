from pydantic import BaseModel
from entitas import ExecuteProcessor, Matcher, Entity  # type: ignore
from agent.chat_request_handler import ChatRequestHandler
import format_string.json_format
from components.components import (
    StageEnvironmentComponent,
    ActorComponent,
    SkillCandidateQueueComponent,
)
from overrides import override
from typing import List, final
from game.tcg_game import TCGGame
from loguru import logger
from tcg_models.v_0_0_1 import Skill


#######################################################################################################################################
@final
class GenSkillsResponse(BaseModel):
    attack: Skill
    defense: Skill
    support: Skill


#######################################################################################################################################
def _generate_gen_skills_prompt(
    current_stage: str,
    current_stage_narration: str,
    # current_story: str,
) -> str:

    gen_skills_response_example = GenSkillsResponse(
        attack=Skill(
            name="攻击技能(能够造成伤害)",
            description="攻击技能描述",
            effect="攻击技能效果",
        ),
        defense=Skill(
            name="防御技能(能够减少伤害)",
            description="防御技能描述",
            effect="防御技能效果",
        ),
        support=Skill(
            name="支援技能(能够提供辅助效果,如回复生命值，增加攻击力等)",
            description="支援技能描述",
            effect="支援技能效果",
        ),
    )

    return f"""# 请根据你的能力情况，生成你的技能
## 当前场景
{current_stage}
### 场景描述
{current_stage_narration}
## 输出要求
### 输出格式(JSON)
{gen_skills_response_example.model_dump_json()}"""


#######################################################################################################################################
@final
class GenSkillCandidateQueueSystem(ExecuteProcessor):

    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    #######################################################################################################################################
    @override
    def execute(self) -> None:
        pass

    #######################################################################################################################################
    @override
    async def a_execute1(self) -> None:
        # pass
        self._clear_all_skill_candidate_queue_components()
        await self._process_actor_planning_request()

    #######################################################################################################################################
    def _clear_all_skill_candidate_queue_components(self) -> None:
        actor_entities = self._game.get_group(
            Matcher(
                all_of=[
                    SkillCandidateQueueComponent,
                ],
            )
        ).entities.copy()

        for entity in actor_entities:
            entity.remove(SkillCandidateQueueComponent)

    #######################################################################################################################################
    async def _process_actor_planning_request(self) -> None:

        # 获取所有需要进行角色规划的角色
        actor_entities = self._game.get_group(
            Matcher(
                all_of=[
                    ActorComponent,
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
                logger.error(f"Agent: {request_handler._name}, Response is empty.")
                continue

            logger.warning(
                f"Agent: {request_handler._name}, Response:\n{request_handler.response_content}"
            )

            entity2 = self._game.get_entity_by_name(request_handler._name)
            assert entity2 is not None
            self._handle_actor_response(entity2, request_handler)

    #######################################################################################################################################
    def _handle_actor_response(
        self, entity2: Entity, request_handler: ChatRequestHandler
    ) -> None:

        try:

            format_response = GenSkillsResponse.model_validate_json(
                format_string.json_format.strip_json_code_block(
                    request_handler.response_content
                )
            )

            entity2.replace(
                SkillCandidateQueueComponent,
                entity2._name,
                [
                    format_response.attack,
                    format_response.defense,
                    format_response.support,
                ],
            )

        except:
            logger.error(
                f"""返回格式错误: {entity2._name}, Response = \n{request_handler.response_content}"""
            )

    #######################################################################################################################################
    def _generate_chat_requests(
        self, actor_entities: set[Entity]
    ) -> List[ChatRequestHandler]:

        request_handlers: List[ChatRequestHandler] = []

        for entity in actor_entities:

            #
            current_stage = self._game.safe_get_stage_entity(entity)
            assert current_stage is not None

            # 生成消息
            message = _generate_gen_skills_prompt(
                current_stage._name,
                current_stage.get(StageEnvironmentComponent).narrate,
                # current_stage.get(StageEnvironmentComponent).story,
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
