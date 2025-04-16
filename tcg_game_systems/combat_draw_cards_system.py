from pydantic import BaseModel
from entitas import ExecuteProcessor, Entity  # type: ignore
from llm_serves.chat_request_handler import ChatRequestHandler
import format_string.json_format
from models_v_0_0_1 import (
    EnvironmentComponent,
    HandComponent,
    HeroComponent,
    MonsterComponent,
    Skill,
    HandDetail,
)
from typing import Final, List, Set, final, override
from loguru import logger
from game.tcg_game import TCGGame


#######################################################################################################################################
@final
class SkillResponse(BaseModel):
    skill: Skill
    targets: List[str]
    reason: str
    dialogue: str


#######################################################################################################################################
@final
class DrawCardsResponse(BaseModel):
    gen_skill_reponse: List[SkillResponse]


#######################################################################################################################################
def _generate_prompt(
    skill_creation_count: int,
    current_stage: str,
    current_stage_narration: str,
    round_turns: List[str],
) -> str:
    assert skill_creation_count > 0
    if skill_creation_count <= 0:
        return ""

    response_example = DrawCardsResponse(
        gen_skill_reponse=[],
    )

    for i in range(skill_creation_count):

        skill_response_example = SkillResponse(
            skill=Skill(
                name=f"技能{i+1}",
                description=f"技能{i+1}描述",
                effect=f"技能{i+1}效果",
            ),
            targets=["目标1", "目标2"],
            reason=f"技能{i+1}使用原因",
            dialogue=f"技能{i+1}对话",
        )

        response_example.gen_skill_reponse.append(skill_response_example)

    return f"""# 请你生成 {skill_creation_count} 个技能，并决定如何使用。
## 当前场景状态
{current_stage} | {current_stage_narration}
## (场景内角色) 行动顺序(从左到右)
{round_turns}
## 输出内容
- 注意，如生成技能提到了属性(生命/物理攻击/物理防御/魔法攻击/魔法防御)，请在技能描述与影响里明确说明改变的数值。
## 输出格式(JSON)
{response_example.model_dump_json()}
### 注意
- 禁用换行/空行。
- 直接输出合规JSON。"""


#######################################################################################################################################
@final
class CombatDrawCardsSystem(ExecuteProcessor):

    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context
        self._skill_creation_count: Final[int] = 2

    ######################################################################################################################################
    @override
    def execute(self) -> None:
        pass

    ######################################################################################################################################
    @override
    async def a_execute1(self) -> None:

        if not self._game.current_engagement.is_on_going_phase:
            logger.error(f"not web_game.current_engagement.is_on_going_phase")
            return

        player_entity = self._game.get_player_entity()
        assert player_entity is not None

        actor_entities = self._game.retrieve_actors_on_stage(player_entity)
        for entity in actor_entities:
            assert entity.has(HeroComponent) or entity.has(
                MonsterComponent
            ), f"{entity._name} must have HeroComponent or MonsterComponent"

        if len(actor_entities) == 0:
            return

        # 先清除
        # self._clear(actor_entities)
        self._game.clear_hands()

        # 处理请求
        await self._process_chat_requests(actor_entities)

    #######################################################################################################################################
    # def _clear(self, actor_entities: Set[Entity]) -> None:
    #     copy_actor_entities = actor_entities.copy()
    #     for entity in copy_actor_entities:
    #         if entity.has(HandComponent):
    #             entity.remove(HandComponent)

    #######################################################################################################################################
    async def _process_chat_requests(self, react_entities: Set[Entity]) -> None:

        # 处理角色规划请求
        request_handlers: List[ChatRequestHandler] = self._generate_requests(
            react_entities
        )

        # 语言服务
        await self._game.chat_system.gather(request_handlers=request_handlers)

        # 处理角色规划请求
        self._handle_responses(request_handlers)

    #######################################################################################################################################
    def _handle_responses(self, request_handlers: List[ChatRequestHandler]) -> None:

        for request_handler in request_handlers:

            if request_handler.response_content == "":
                continue

            entity2 = self._game.get_entity_by_name(request_handler._name)
            assert entity2 is not None
            self._handle_response(entity2, request_handler)

    #######################################################################################################################################
    def _handle_response(
        self, entity2: Entity, request_handler: ChatRequestHandler
    ) -> None:

        try:

            format_response = DrawCardsResponse.model_validate_json(
                format_string.json_format.strip_json_code_block(
                    request_handler.response_content
                )
            )

            skills: List[Skill] = [
                skill_response.skill
                for skill_response in format_response.gen_skill_reponse
            ]

            details: List[HandDetail] = [
                HandDetail(
                    skill=skill_response.skill.name,
                    targets=skill_response.targets,
                    reason=skill_response.reason,
                    dialogue=skill_response.dialogue,
                )
                for skill_response in format_response.gen_skill_reponse
            ]

            entity2.replace(
                HandComponent,
                entity2._name,
                skills,
                details,
            )

        except Exception as e:
            logger.error(f"Exception: {e}")

    #######################################################################################################################################
    def _generate_requests(
        self, actor_entities: set[Entity]
    ) -> List[ChatRequestHandler]:

        request_handlers: List[ChatRequestHandler] = []

        last_round = self._game.current_engagement.last_round
        assert (
            not last_round.is_round_complete
        ), f"last_round.is_round_complete: {last_round.is_round_complete}"

        for entity in actor_entities:

            #
            current_stage = self._game.safe_get_stage_entity(entity)
            assert current_stage is not None

            # 生成消息
            message = _generate_prompt(
                self._skill_creation_count,
                current_stage._name,
                current_stage.get(EnvironmentComponent).narrate,
                last_round.round_turns,
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
