from overrides import override
from agent.chat_request_handler import ChatRequestHandler
from entitas import ExecuteProcessor, Matcher  # type: ignore
from entitas.entity import Entity
from game.tcg_game_context import TCGGameContext
from game.tcg_game import TCGGame
from typing import Deque, List, Optional, Set, final, cast
from rpg_models.event_models import AnnounceEvent
from tcg_models.v_0_0_1 import (
    ActorInstance,
    ActiveSkill,
    BuffTriggerType,
    HitInfo,
    HitType,
    DamageType,
)
from components.components import (
    AttributeCompoment,
    ActorComponent,
    FinalAppearanceComponent,
    StageEnvironmentComponent,
    WorldSystemComponent,
)
from loguru import logger
import json


class B5_ExecuteHitsSystem(ExecuteProcessor):

    def __init__(self, context: TCGGameContext) -> None:
        self._context: TCGGameContext = context
        self._game: TCGGame = cast(TCGGame, context._game)
        assert self._game is not None

    async def a_execute1(self) -> None:
        await self._process()

    async def _process(self) -> None:
        if self._game._battle_manager._new_turn_flag:
            return
        if self._game._battle_manager._battle_end_flag:
            return
        if len(self._game._battle_manager._order_queue) is 0:
            return
        if len(self._game._battle_manager._hits_stack) is 0:
            return

        done_hits_log: str = ""
        # 执行stack里的所有hit
        while len(self._game._battle_manager._hits_stack) > 0:
            hit = self._game._battle_manager._hits_stack.pop()
            self._execute_hit(hit)
            # 添加历史
            self._game._battle_manager.add_history(hit.log)
            done_hits_log += hit.log

        # pop掉当前行动角色，删掉所有行动力小于0的
        temp_actor_name = self._game._battle_manager._order_queue.popleft()
        for actor_name in self._game._battle_manager._order_queue:
            actor = self._context.get_entity_by_name(actor_name)
            assert actor is not None
            comp = actor.get(AttributeCompoment)
            assert comp is not None
            if comp.action_times <= 0:
                self._game._battle_manager._order_queue.remove(actor_name)

        # 问世界系统，给我生成一段描述
        # 得到所有角色和场景信息
        temp_actor = self._context.get_entity_by_name(temp_actor_name)
        assert temp_actor is not None
        current_stage = self._context.safe_get_stage_entity(temp_actor)
        assert current_stage is not None
        actors_set = self._game.retrieve_actors_on_stage(current_stage)
        actors_info_list: List[str] = [
            f"{actor._name}：\n外表：{actor.get(FinalAppearanceComponent).final_appearance}\n生命值：{actor.get(AttributeCompoment).hp}/{actor.get(AttributeCompoment).maxhp}\n行动力：{actor.get(AttributeCompoment).action_times}/{actor.get(AttributeCompoment).max_action_times}"
            for actor in actors_set
            if actor.has(FinalAppearanceComponent)
        ]
        msg = _gen_prompt(
            current_stage_name=current_stage._name,
            current_stage_narration=current_stage.get(
                StageEnvironmentComponent
            ).narrate,
            actors_info_list=actors_info_list,
            act_order=self._game._battle_manager._order_queue.copy(),
            done_hits_log=done_hits_log,
        )
        world_system_entity = self._get_world_system()
        assert world_system_entity is not None
        request_handlers: List[ChatRequestHandler] = []
        agent_short_term_memory = self._game.get_agent_short_term_memory(
            world_system_entity
        )
        request_handlers.append(
            ChatRequestHandler(
                name=world_system_entity._name,
                prompt=msg,
                chat_history=agent_short_term_memory.chat_history,
            )
        )
        await self._game.langserve_system.gather(request_handlers=request_handlers)
        self._game.append_human_message(world_system_entity, msg)
        self._game.append_ai_message(
            world_system_entity, request_handlers[0].response_content
        )
        # 把描述添加进历史
        self._game._battle_manager.add_history(request_handlers[0].response_content)

    def _execute_hit(self, hit: HitInfo) -> None:
        source_name = hit.source
        target_name = hit.target
        source = self._context.get_entity_by_name(source_name)
        target = self._context.get_entity_by_name(target_name)
        if source is None:
            assert False, "source is None"
        if target is None:
            assert False, "target is None"
        source_comp = source.get(AttributeCompoment)
        target_comp = target.get(AttributeCompoment)
        if source_comp is None:
            assert False, "source_comp is None"
        if target_comp is None:
            assert False, "target_comp is None"
        actor_comp = source.get(ActorComponent)
        if actor_comp is None:
            assert False, "actor_comp is None"
        stage_name = actor_comp.current_stage

        # 执行hit
        if hit.type is HitType.NONE:
            assert False, "hit type is NONE"
        # 如果是个伤害行为
        elif hit.type is HitType.DAMAGE:
            value = hit.value
            # 检查被攻击时触发的buff，应该包装个新函数
            for buff, last_time in target_comp.buffs.items():
                if buff.timing is BuffTriggerType.ON_ATTACKED:
                    match buff.name:
                        case "护盾":
                            value = int(value * 0.5)
                            hit.log += (
                                f"{target_name} 由于 {buff.name} 的效果抵挡了伤害。"
                            )
                        case "藤甲":
                            value = 1
                            hit.log += (
                                f"{target_name} 由于 {buff.name} 的效果抵挡了伤害。"
                            )
            # 记录log
            hit.log += f"{source_name} 对 {target_name} 造成了 {value} 点伤害。"
            # 扣血
            hp_value = target_comp.hp - value
            hp_value = hp_value if hp_value >= 0 else 0
        # 如果是个加血行为
        elif hit.type is HitType.HEAL:
            value = hit.value
            # 记录log
            hit.log += f"{source_name} 对 {target_name} 治疗了 {value} 点生命。"
            # 加血
            hp_value = target_comp.hp + value
            hp_value = hp_value if hp_value <= target_comp.maxhp else target_comp.maxhp
        # 如果是个加buff行为
        elif hit.type is HitType.ADDBUFF:
            if hit.buff is None:
                assert False, "buff is None"
            buff = hit.buff
            # 记录log
            hit.log += f"{source_name} 对 {target_name} 施加了 {buff.name}。"
            # 加buff
            target_comp.buffs[buff] = hit.value
            hp_value = target_comp.hp
        # 如果是个减buff行为
        elif hit.type is HitType.REMOVEBUFF:
            if hit.buff is None:
                assert False, "buff is None"
            buff = hit.buff
            # 判断有没有要减的buff
            if buff in target_comp.buffs:
                # 记录log
                hit.log += f"{source_name} 对 {target_name} 解除了 {buff.name}。"
                # 减buff
                del target_comp.buffs[buff]
            else:
                hit.log += f"{target_name} 没有 {buff.name}。"
            hp_value = target_comp.hp

        # 修改血量, 广播说话
        self._modify_hp_action_times_and_announce(
            source, hp_value, hit.text, stage_name
        )

    def _modify_hp_action_times_and_announce(
        self, actor: Entity, hp: int, text: str, stage_name: str
    ) -> None:
        actor_comp = actor.get(AttributeCompoment)
        if actor_comp is None:
            assert False, "actor_comp is None"
        actor.replace(
            AttributeCompoment,
            actor_comp.name,
            hp,
            actor_comp.maxhp,
            actor_comp.action_times - 1,
            actor_comp.max_action_times,
            actor_comp.strength,
            actor_comp.agility,
            actor_comp.wisdom,
            actor_comp.buffs,
            actor_comp.active_skills,
            actor_comp.trigger_skills,
        )
        self._game.broadcast_event(
            actor,
            AnnounceEvent(
                message=f"{actor_comp.name}说：",
                announcer_name=actor_comp.name,
                stage_name=stage_name,
                content=text,
            ),
        )

    def _get_world_system(self) -> Optional[Entity]:

        entities: Set[Entity] = self._context.get_group(
            Matcher(
                any_of=[WorldSystemComponent],
            )
        ).entities

        if len(entities) > 0:
            return next(iter(entities))

        return None


def _gen_prompt(
    current_stage_name: str,
    current_stage_narration: str,
    actors_info_list: List[str],
    act_order: Deque[str],
    done_hits_log: str,
) -> str:
    return f"""
# 请作为战斗系统的故事讲述者，描述这轮的战斗情况。
## 战场形势
### 当前所在的场景
{current_stage_name}
### 当前场景描述
{current_stage_narration}
### 当前场景内所有角色的状态
{"\n".join(actors_info_list)}
### 本回合尚未未行动角色行动顺序队列
{", ".join(f"{index}: {item}" for index, item in enumerate(act_order))}
### 本轮中发生的行动
{done_hits_log}
## 描述要求
1. 战斗过程的描述需要生动和有趣。
2. 必须充分考虑每个角色的性格，不要让角色成为只会战斗的棋子。
"""
