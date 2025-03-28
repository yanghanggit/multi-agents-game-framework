from entitas import Entity, Matcher, ExecuteProcessor  # type: ignore
from overrides import override
from components.components_v_0_0_1 import (
    WorldSystemComponent,
    StageComponent,
    ActorComponent,
    KickOffMessageComponent,
    KickOffDoneComponent,
    # SystemMessageComponent,
    StageEnvironmentComponent,
    HeroComponent,
    MonsterComponent,
    HomeComponent,
    MonsterComponent,
    DungeonComponent,
)
from typing import Dict, Set, final, List
from game.tcg_game import TCGGame

# from loguru import logger
from extended_systems.chat_request_handler import ChatRequestHandler


###############################################################################################################################################
def _generate_actor_kick_off_prompt(kick_off_message: str) -> str:
    return f"""# 游戏启动! 你将开始你的扮演。你将以此为初始状态，开始你的冒险。
## 这是你的启动消息
{kick_off_message}
## 输出要求
- 你的内心活动，单段紧凑自述（禁用换行/空行）"""


###############################################################################################################################################
def _generate_stage_kick_off_prompt(
    kick_off_message: str,
) -> str:
    return f"""# 游戏启动! 你将开始你的扮演。你将以此为初始状态，开始你的冒险。
## 这是你的启动消息
{kick_off_message}
## 输出要求
- 输出场景描述，单段紧凑自述（禁用换行/空行）"""


###############################################################################################################################################
def _generate_world_system_kick_off_prompt() -> str:
    return f"""# 游戏启动! 你将开始你的扮演。你将以此为初始状态，开始你的冒险。
## 这是你的启动消息
- 请回答你的职能与描述。
## 输出要求
- 确认你的职能，单段紧凑自述（禁用换行/空行）"""


###############################################################################################################################################


###############################################################################################################################################
@final
class KickOffSystem(ExecuteProcessor):

    ###############################################################################################################################################
    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    ###############################################################################################################################################
    @override
    def execute(self) -> None:
        pass

    ###############################################################################################################################################
    @override
    async def a_execute1(self) -> None:

        entities: Set[Entity] = set()

        # 获取世界系统实体
        world_system_entities = self._retrieve_world_system_entities_for_kick_off()
        entities.update(world_system_entities)

        # 获取舞台实体
        stage_entities = self._retrieve_stage_entities_for_kick_off()
        entities.update(stage_entities)

        # 获取角色实体
        actor_entities = self._retrieve_actor_entities_for_kick_off()
        entities.update(actor_entities)

        if len(entities) == 0:
            return

        # 处理请求
        await self._process_request(entities)

        # 设置第一次观察
        self._setup_heros_first_observation()

    ###############################################################################################################################################
    def _retrieve_world_system_entities_for_kick_off(self) -> Set[Entity]:
        ret: Set[Entity] = set()
        world_entities = self._game.get_group(
            Matcher(
                all_of=[WorldSystemComponent, KickOffMessageComponent],
                none_of=[KickOffDoneComponent],
            )
        ).entities.copy()

        for world_system_entity in world_entities:
            assert not world_system_entity.has(KickOffDoneComponent)
            assert world_system_entity.has(KickOffMessageComponent)
            kick_off_message_comp = world_system_entity.get(KickOffMessageComponent)
            if kick_off_message_comp.content == "":
                continue

            ret.add(world_system_entity)

        return ret

    ###############################################################################################################################################
    def _retrieve_stage_entities_for_kick_off(self) -> Set[Entity]:

        ret: Set[Entity] = set()

        # 获取玩家实体
        player_entity = self._game.get_player_entity()
        assert player_entity is not None

        # 获取玩家所在的舞台实体
        player_stage_entity = self._game.safe_get_stage_entity(player_entity)
        assert player_stage_entity is not None

        if player_stage_entity.has(KickOffDoneComponent):
            # 已经完成了kick off
            return ret

        assert player_stage_entity.has(KickOffMessageComponent)
        kick_off_message_comp = player_stage_entity.get(KickOffMessageComponent)
        if kick_off_message_comp.content == "":
            # 没有kick off消息
            return ret

        if player_stage_entity.has(DungeonComponent):
            # 如果是副本场景，直接返回
            return ret

        ret.add(player_stage_entity)
        return ret

    ###############################################################################################################################################
    def _retrieve_actor_entities_for_kick_off(self) -> Set[Entity]:
        ret: Set[Entity] = set()

        # 获取玩家实体
        player_entity = self._game.get_player_entity()
        assert player_entity is not None

        # 获取玩家所在的舞台实体
        player_stage_entity = self._game.safe_get_stage_entity(player_entity)
        assert player_stage_entity is not None

        actors_on_stage = self._game.retrieve_actors_on_stage(player_stage_entity)
        for actor_entity in actors_on_stage:
            if actor_entity.has(KickOffDoneComponent):
                # 已经完成了kick off
                continue

            assert actor_entity.has(KickOffMessageComponent)
            kick_off_message_comp = actor_entity.get(KickOffMessageComponent)
            if kick_off_message_comp.content == "":
                # 没有kick off消息
                continue

            if actor_entity.has(MonsterComponent):
                # 如果是怪物，直接跳过
                continue

            #
            ret.add(actor_entity)

        return ret

    ###############################################################################################################################################
    async def _process_request(self, entities: Set[Entity]) -> None:

        # 添加请求处理器
        request_handlers: List[ChatRequestHandler] = []

        for entity1 in entities:
            # 不同实体生成不同的提示
            gen_prompt = self._generate_prompt(entity1)
            if gen_prompt == "":
                continue

            agent_short_term_memory = self._game.get_agent_short_term_memory(entity1)
            request_handlers.append(
                ChatRequestHandler(
                    name=entity1._name,
                    prompt=gen_prompt,
                    chat_history=agent_short_term_memory.chat_history,
                )
            )

        # 并发
        await self._game.langserve_system.gather(request_handlers=request_handlers)

        # 添加上下文。
        for request_handler in request_handlers:

            entity2 = self._game.get_entity_by_name(request_handler._name)
            assert entity2 is not None

            if request_handler.response_content == "":
                continue

            self._game.append_human_message(entity2, request_handler._prompt)
            self._game.append_ai_message(entity2, request_handler.response_content)

            # 必须执行
            entity2.replace(KickOffDoneComponent, entity2._name)

            # 若是场景，用response替换narrate
            if entity2.has(StageComponent):
                entity2.replace(
                    StageEnvironmentComponent,
                    entity2._name,
                    request_handler.response_content,
                )
            elif entity2.has(ActorComponent):
                assert entity2.has(HeroComponent) or entity2.has(MonsterComponent)

    ###############################################################################################################################################
    def _generate_prompt(self, entity: Entity) -> str:

        kick_off_message_comp = entity.get(KickOffMessageComponent)
        assert kick_off_message_comp is not None
        kick_off_message = kick_off_message_comp.content

        # 不同实体生成不同的提示
        gen_prompt = ""
        if entity.has(ActorComponent):
            # 角色的
            gen_prompt = _generate_actor_kick_off_prompt(kick_off_message)
        elif entity.has(StageComponent):
            # 舞台的
            gen_prompt = _generate_stage_kick_off_prompt(
                kick_off_message,
            )
        elif entity.has(WorldSystemComponent):
            # 世界系统的
            gen_prompt = _generate_world_system_kick_off_prompt()

        return gen_prompt

    ###############################################################################################################################################
    def _setup_heros_first_observation(self) -> None:
        # 第一次观察 周围的环境。
        hero_entities: Set[Entity] = self._game.get_group(
            Matcher(
                all_of=[KickOffDoneComponent, HeroComponent],
            )
        ).entities
        # 只有在家的场景才需要第一次观察！做一些memory的初始化工作。
        for hero_entity in hero_entities:
            self._setup_hero_first_observation(hero_entity)

    ###############################################################################################################################################
    # TODO 第一次观察所在场景已经场景内都有谁
    def _setup_hero_first_observation(self, actor_entity: Entity) -> None:
        assert actor_entity.has(ActorComponent)
        assert actor_entity.has(HeroComponent)
        stage_entity = self._game.safe_get_stage_entity(actor_entity)
        assert stage_entity is not None
        if not stage_entity.has(HomeComponent):
            # 只有在家的场景才需要第一次观察！做一些memory的初始化工作。
            # 其他场景不需要。
            return

        stage_env_comp = stage_entity.get(StageEnvironmentComponent)

        # 获取场景内角色的外貌信息
        actors_appearances_mapping: Dict[str, str] = (
            self._game.retrieve_actor_appearance_on_stage_mapping(actor_entity)
        )
        # 删除自己
        actors_appearances_mapping.pop(actor_entity._name, None)

        # 组织提示词数据
        actors_appearances_info = []
        for actor_name, appearance in actors_appearances_mapping.items():
            actors_appearances_info.append(f"- {actor_name}: {appearance}")
        if len(actors_appearances_info) == 0:
            actors_appearances_info.append("- 无")

        message = f"""# 提示！你进行观察场景
## 所在场景
{stage_entity._name}
## 场景描述
{stage_env_comp.narrate}
## 场景内角色外貌信息
{"\n".join(actors_appearances_info)}"""

        self._game.append_human_message(actor_entity, message)

    ###############################################################################################################################################
