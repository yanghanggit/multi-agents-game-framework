import random
from entitas import Matcher, Entity, Matcher, ExecuteProcessor  # type: ignore
from components.components_v_0_0_1 import (
    HandComponent,
)
from overrides import override
from typing import List, Tuple, final
from game.tcg_game import TCGGame
from components.actions_v_0_0_1 import TurnAction


#######################################################################################################################################
@final
class DungeonCombatRoundSystem(ExecuteProcessor):

    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    #######################################################################################################################################
    @override
    def execute(self) -> None:

        if not self._game.combat_system.is_on_going_phase:
            return  # 不是本阶段就直接返回

        actor_entities = self._game.get_group(
            Matcher(
                all_of=[
                    HandComponent,
                ],
            )
        ).entities

        if len(actor_entities) == 0:
            return

        # 回合增加一次
        self._game.combat_system.new_round()

        # 随机出手顺序
        shuffled_reactive_entities = self._shuffle_action_order(list(actor_entities))
        round_turns: List[str] = [entity._name for entity in shuffled_reactive_entities]
        for _, name in enumerate(round_turns):
            entity2 = self._game.get_entity_by_name(name)
            assert entity2 is not None
            assert not entity2.has(TurnAction)
            # 添加这个动作。
            entity2.replace(
                TurnAction,
                entity2._name,
                len(self._game.combat_system.rounds),
                round_turns,
            )

    #######################################################################################################################################
    # 随机排序
    def _shuffle_action_order(self, react_entities: List[Entity]) -> List[Entity]:
        shuffled_reactive_entities = react_entities.copy()
        random.shuffle(shuffled_reactive_entities)
        return shuffled_reactive_entities

    #######################################################################################################################################
    # 正式的排序方式，按着敏捷度排序
    def _sort_action_order_by_dex(self, react_entities: List[Entity]) -> List[Entity]:

        actor_dexterity_pairs: List[Tuple[Entity, int]] = []
        for entity in react_entities:
            actor_instance = self._game.retrieve_actor_instance(entity)
            assert actor_instance is not None
            actor_dexterity_pairs.append(
                (entity, actor_instance.base_attributes.dexterity)
            )

        return [
            entity
            for entity, _ in sorted(
                actor_dexterity_pairs, key=lambda x: x[1], reverse=True
            )
        ]

    #######################################################################################################################################
