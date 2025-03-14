# from overrides import override
# from agent.chat_request_handler import ChatRequestHandler
# from entitas import ExecuteProcessor, Matcher  # type: ignore
# from entitas.entity import Entity

# # from game.tcg_game_context import TCGGameContext
# from game.tcg_game import TCGGame
# from typing import Deque, List, Optional
# from rpg_models.event_models import AnnounceEvent
# from tcg_models.v_0_0_1 import (
#     # ActorInstance,
#     # ActiveSkill,
#     TriggerType,
#     HitInfo,
#     HitType,
#     DamageType,
# )
# from components.components import (
#     AttributeCompoment,
#     ActorComponent,
#     FinalAppearanceComponent,
#     StageEnvironmentComponent,
#     # WorldSystemComponent,
# )

# # from loguru import logger
# # import json


# class B5_ExecuteHitsSystem(ExecuteProcessor):

#     def __init__(self, game_context: TCGGame) -> None:
#         self._game: TCGGame = game_context

#     @override
#     def execute(self) -> None:
#         pass

#     async def a_execute1(self) -> None:
#         await self._process()

#     async def _process(self) -> None:
#         if self._game._battle_manager._new_turn_flag:
#             return
#         if self._game._battle_manager._battle_end_flag:
#             return
#         if len(self._game._battle_manager._order_queue) == 0:
#             return
#         if len(self._game._battle_manager._hits_stack.stack) == 0:
#             return

#         done_hits_log: str = ""
#         # 执行stack里的所有hit
#         while len(self._game._battle_manager._hits_stack.stack) > 0:
#             hit = self._game._battle_manager._hits_stack.stack.pop()
#             if hit.is_event:
#                 self._execute_event_hit(hit)
#             else:
#                 self._execute_hit(hit)
#             # 添加历史
#             self._game._battle_manager.add_history(hit.log)
#             done_hits_log += hit.log

#         # pop掉当前行动角色，删掉所有行动力小于0的和翘辫子的
#         temp_actor_name = self._game._battle_manager._order_queue.popleft()
#         remove_list = []
#         for actor_name in self._game._battle_manager._order_queue:
#             actor = self._game.get_entity_by_name(actor_name)
#             assert actor is not None
#             comp = actor.get(AttributeCompoment)
#             assert comp is not None
#             if comp.action_times <= 0 or comp.hp <= 0:
#                 remove_list.append(actor_name)
#         for name in remove_list:
#             if name in self._game._battle_manager._order_queue:
#                 self._game._battle_manager._order_queue.remove(name)

#         # 问世界系统，给我生成一段描述
#         # 得到所有角色和场景信息
#         temp_actor = self._game.get_entity_by_name(temp_actor_name)
#         assert temp_actor is not None
#         current_stage = self._game.safe_get_stage_entity(temp_actor)
#         assert current_stage is not None
#         actors_set = self._game.retrieve_actors_on_stage(current_stage)
#         actors_info_list: List[str] = [
#             f"{actor._name}：\n外表：{actor.get(FinalAppearanceComponent).final_appearance}\n生命值：{actor.get(AttributeCompoment).hp}/{actor.get(AttributeCompoment).maxhp}\n行动力：{actor.get(AttributeCompoment).action_times}/{actor.get(AttributeCompoment).max_action_times}"
#             for actor in actors_set
#             if actor.has(FinalAppearanceComponent)
#         ]
#         msg = _gen_prompt(
#             current_stage_name=current_stage._name,
#             current_stage_narration=current_stage.get(
#                 StageEnvironmentComponent
#             ).narrate,
#             actors_info_list=actors_info_list,
#             act_order=self._game._battle_manager._order_queue.copy(),
#             done_hits_log=done_hits_log,
#             battle_history=self._game._battle_manager._battle_history.model_dump_json(),
#         )
#         world_system_entity = self._get_world_system()
#         assert world_system_entity is not None
#         request_handlers: List[ChatRequestHandler] = []
#         agent_short_term_memory = self._game.get_agent_short_term_memory(
#             world_system_entity
#         )
#         request_handlers.append(
#             ChatRequestHandler(
#                 name=world_system_entity._name,
#                 prompt=msg,
#                 chat_history=agent_short_term_memory.chat_history,
#             )
#         )
#         await self._game.langserve_system.gather(request_handlers=request_handlers)
#         # self._game.append_human_message(world_system_entity, msg)
#         # self._game.append_ai_message(
#         #     world_system_entity, request_handlers[0].response_content
#         # )

#         # 把描述添加进历史
#         self._game._battle_manager.add_history(request_handlers[0].response_content)

#     def _execute_hit(self, hit: HitInfo) -> bool:
#         source_name = hit.source
#         target_name = hit.target
#         source = self._game.get_entity_by_name(source_name)
#         target = self._game.get_entity_by_name(target_name)
#         if source is None:
#             assert False, "source is None"
#         if target is None:
#             assert False, "target is None"
#         source_comp = source.get(AttributeCompoment)
#         target_comp = target.get(AttributeCompoment)
#         if source_comp is None:
#             assert False, "source_comp is None"
#         if target_comp is None:
#             assert False, "target_comp is None"
#         actor_comp = source.get(ActorComponent)
#         if actor_comp is None:
#             assert False, "actor_comp is None"

#         # 检查source和target是不是死了
#         if source_comp.hp <= 0:
#             hit.log += f"{source_name} 已经被击败，无法行动！"
#             return False
#         if target_comp.hp <= 0:
#             hit.log += f"目标已被击败！"
#             return False
#         # 检查source是不是没行动力了
#         if source_comp.action_times <= 0 and hit.is_cost:
#             hit.log += f"{source_name} 行动力不足，无法继续行动！"
#             return False

#         hp_value = target_comp.hp
#         # 执行hit
#         if hit.type == HitType.NONE:
#             assert False, "hit type is NONE"
#         # 如果是个伤害行为
#         elif hit.type == HitType.DAMAGE:
#             value = hit.value
#             # 检查被攻击时触发的buff，移除失效的buff，应该包装个新函数
#             remove_list = []
#             for buff_name, last_time in target_comp.buffs.items():
#                 buff = self._game.world.boot.data_base.buffs[buff_name]
#                 if buff.timing == TriggerType.ON_ATTACKED:
#                     match buff.name:
#                         case "护盾":
#                             if hit.dmgtype == DamageType.PHYSICAL:
#                                 value = int(value * 0.5)
#                                 hit.log += (
#                                     f"{target_name} 由于 {buff.name} 的效果抵挡了伤害。"
#                                 )
#                         case "藤甲":
#                             if hit.dmgtype == DamageType.PHYSICAL:
#                                 value = 1
#                                 hit.log += (
#                                     f"{target_name} 由于 {buff.name} 的效果抵挡了伤害。"
#                                 )
#                             elif hit.dmgtype == DamageType.FIRE:
#                                 value = int(value * 1.5)
#                                 hit.log += f"{target_name} 由于 {buff.name} 的效果增强了伤害。{buff.name} 被移除了！"
#                                 remove_list.append(buff_name)
#             for name in remove_list:
#                 target_comp.buffs.pop(name)

#             # 记录log
#             hit.log += f"{source_name} 对 {target_name} 造成了 {value} 点伤害。"
#             # 扣血
#             hp_value = target_comp.hp - value
#             hp_value = hp_value if hp_value > 0 else 0
#             if hp_value == 0:
#                 hit.log += f"{target_name} 被击败了！"
#         # 如果是个加血行为
#         elif hit.type == HitType.HEAL:
#             value = hit.value
#             # 记录log
#             hit.log += f"{source_name} 对 {target_name} 治疗了 {value} 点生命。"
#             # 加血
#             hp_value = target_comp.hp + value
#             hp_value = hp_value if hp_value <= target_comp.maxhp else target_comp.maxhp
#         # 如果是个加buff行为
#         elif hit.type == HitType.ADDBUFF:
#             if hit.buff is None:
#                 assert False, "buff is None"
#             buff = hit.buff
#             # 记录log
#             hit.log += f"{source_name} 对 {target_name} 施加了 {buff.name}。"
#             # 加buff
#             target_comp.buffs[buff.name] = hit.value
#             hp_value = target_comp.hp
#         # 如果是个减buff行为
#         elif hit.type == HitType.REMOVEBUFF:
#             if hit.buff is None:
#                 assert False, "buff is None"
#             buff = hit.buff
#             # 判断有没有要减的buff
#             if buff.name in target_comp.buffs:
#                 # 记录log
#                 hit.log += f"{source_name} 对 {target_name} 解除了 {buff.name}。"
#                 # 减buff
#                 del target_comp.buffs[buff.name]
#             else:
#                 hit.log += f"{target_name} 没有 {buff.name}。"
#             hp_value = target_comp.hp

#         # 修改血量, 减行动力，广播说话，广播战斗log
#         stage_name = actor_comp.current_stage
#         self._modify_hp_action_times_and_announce(
#             source,
#             target,
#             hp_value,
#             hit.text,
#             stage_name,
#             hit.is_cost,
#             hit.log,
#         )
#         return True

#     def _execute_event_hit(self, hit: HitInfo) -> bool:
#         target_name = hit.target
#         target = self._game.get_entity_by_name(target_name)
#         if target is None:
#             assert False, "target is None"
#         target_comp = target.get(AttributeCompoment)
#         if target_comp is None:
#             assert False, "target_comp is None"

#         # target是不是死了
#         if target_comp.hp <= 0:
#             hit.log += f"目标已被击败！"
#             return False

#         hp_value = target_comp.hp
#         # 执行hit
#         if hit.type == HitType.NONE:
#             assert False, "hit type is NONE"
#         # 如果是个伤害行为
#         elif hit.type == HitType.DAMAGE:
#             value = hit.value
#             # 检查被攻击时触发的buff，移除失效的buff，应该包装个新函数
#             remove_list = []
#             for buff_name, last_time in target_comp.buffs.items():
#                 buff = self._game.world.boot.data_base.buffs[buff_name]
#                 if buff.timing == TriggerType.ON_ATTACKED:
#                     match buff.name:
#                         case "护盾":
#                             if hit.dmgtype == DamageType.PHYSICAL:
#                                 value = int(value * 0.5)
#                                 hit.log += (
#                                     f"{target_name} 由于 {buff.name} 的效果抵挡了伤害。"
#                                 )
#                         case "藤甲":
#                             if hit.dmgtype == DamageType.PHYSICAL:
#                                 value = 1
#                                 hit.log += (
#                                     f"{target_name} 由于 {buff.name} 的效果抵挡了伤害。"
#                                 )
#                             elif hit.dmgtype == DamageType.FIRE:
#                                 value = int(value * 1.5)
#                                 hit.log += f"{target_name} 由于 {buff.name} 的效果增强了伤害。{buff.name} 被移除了！"
#                                 remove_list.append(buff_name)
#             for name in remove_list:
#                 target_comp.buffs.pop(name)

#             # 记录log
#             hit.log += f"{hit.source} 对 {target_name} 造成了 {value} 点伤害。"
#             # 扣血
#             hp_value = target_comp.hp - value
#             hp_value = hp_value if hp_value > 0 else 0
#             if hp_value == 0:
#                 hit.log += f"{target_name} 被击败了！"
#         # 如果是个加血行为
#         elif hit.type == HitType.HEAL:
#             value = hit.value
#             # 记录log
#             hit.log += f"{hit.source} 对 {target_name} 治疗了 {value} 点生命。"
#             # 加血
#             hp_value = target_comp.hp + value
#             hp_value = hp_value if hp_value <= target_comp.maxhp else target_comp.maxhp
#         # 如果是个加buff行为
#         elif hit.type == HitType.ADDBUFF:
#             if hit.buff is None:
#                 assert False, "buff is None"
#             buff = hit.buff
#             # 记录log
#             hit.log += f"{hit.source} 对 {target_name} 施加了 {buff.name}。"
#             # 加buff
#             target_comp.buffs[buff.name] = hit.value
#             hp_value = target_comp.hp
#         # 如果是个减buff行为
#         elif hit.type == HitType.REMOVEBUFF:
#             if hit.buff is None:
#                 assert False, "buff is None"
#             buff = hit.buff
#             # 判断有没有要减的buff
#             if buff.name in target_comp.buffs:
#                 # 记录log
#                 hit.log += f"{hit.source} 对 {target_name} 解除了 {buff.name}。"
#                 # 减buff
#                 del target_comp.buffs[buff.name]
#             else:
#                 hit.log += f"{target_name} 没有 {buff.name}。"
#             hp_value = target_comp.hp

#         # 修改血量, 减行动力，广播说话，广播战斗log
#         stage_entity = self._game.get_current_stage_entity()
#         assert stage_entity is not None
#         stage_name = stage_entity._name
#         self._modify_hp_action_times_and_announce(
#             target,
#             target,
#             hp_value,
#             hit.text,
#             stage_name,
#             hit.is_cost,
#             hit.log,
#         )
#         return True

#     def _modify_hp_action_times_and_announce(
#         self,
#         source: Entity,
#         target: Entity,
#         hp: int,
#         text: str,
#         stage_name: str,
#         reduce_action_times: bool,
#         log: str,
#     ) -> None:
#         source_comp = source.get(AttributeCompoment)
#         target_comp = target.get(AttributeCompoment)
#         if source_comp is None:
#             assert False, "source_comp is None"
#         if target_comp is None:
#             assert False, "target_comp is None"
#         # 掉行动力
#         if reduce_action_times:
#             source.replace(
#                 AttributeCompoment,
#                 source_comp.name,
#                 source_comp.hp,
#                 source_comp.maxhp,
#                 source_comp.action_times - 1,
#                 source_comp.max_action_times,
#                 source_comp.strength,
#                 source_comp.agility,
#                 source_comp.wisdom,
#                 source_comp.buffs,
#                 source_comp.active_skills,
#                 source_comp.trigger_skills,
#             )
#         # 改血量
#         target.replace(
#             AttributeCompoment,
#             target_comp.name,
#             hp,
#             target_comp.maxhp,
#             target_comp.action_times,
#             target_comp.max_action_times,
#             target_comp.strength,
#             target_comp.agility,
#             target_comp.wisdom,
#             target_comp.buffs,
#             target_comp.active_skills,
#             target_comp.trigger_skills,
#         )
#         if text != "":
#             self._game.broadcast_event(
#                 source,
#                 AnnounceEvent(
#                     message=f"{source._name}说：" + text,
#                     announcer_name=source._name,
#                     stage_name=stage_name,
#                     content=text,
#                 ),
#             )

#         if log != "":
#             self._game.broadcast_event(
#                 source,
#                 AnnounceEvent(
#                     message="发生事件：" + log,
#                     announcer_name="系统",
#                     stage_name=stage_name,
#                     content=log,
#                 ),
#             )

#     def _get_world_system(self, name: str = "战斗系统") -> Optional[Entity]:
#         return self._game.get_world_entity(name)


# def _gen_prompt(
#     current_stage_name: str,
#     current_stage_narration: str,
#     actors_info_list: List[str],
#     act_order: Deque[str],
#     done_hits_log: str,
#     battle_history: str,
# ) -> str:
#     return f"""
# # 请作为战斗系统的故事讲述者，参考战斗日志，描述此刻的战斗情况。
# ## 战场形势
# ### 当前所在的场景
# {current_stage_name}
# ### 当前场景描述
# {current_stage_narration}
# ### 当前场景内所有角色的状态
# {"\n".join(actors_info_list)}
# ### 本回合尚未未行动角色行动顺序队列
# {", ".join(f"{index}: {item}" for index, item in enumerate(act_order))}
# ### 此刻发生的行动
# {done_hits_log}
# ### 截至目前，整场战斗的记录
# {battle_history}
# ## 描述要求
# 1. 战斗过程的描述需要生动和有趣。
# 2. 描述中不要附带角色对话，不要揣测角色心理活动，仅以第三人称视角对发生的事件做客观描述。
# 3. 尽量将描述的长度限制在三到五句话左右。
# 4. 本轮中发生的动作的执行者和目标必须在描述中出现，且选二者之一作为描述的主体。
# 5. 不要预测尚未发生的事。
# 6. 描述需要客观公正，不要在价值观上偏袒任何一方。
# """
