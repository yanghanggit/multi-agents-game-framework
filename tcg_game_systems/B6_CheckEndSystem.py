from overrides import override
from entitas import ExecuteProcessor, Matcher  # type: ignore
from game.tcg_game_context import TCGGameContext
from game.tcg_game import TCGGame
from typing import cast

from components.components import (
    AttributeCompoment,
    ActorComponent,
    HeroActorFlagComponent,
    MonsterActorFlagComponent,
)
from loguru import logger


class B6_CheckEndSystem(ExecuteProcessor):

    def __init__(self, context: TCGGameContext) -> None:
        self._context: TCGGameContext = context
        self._game: TCGGame = cast(TCGGame, context._game)
        assert self._game is not None

    @override
    def execute(self) -> None:
        if self._game._battle_manager._new_turn_flag:
            return
        if self._game._battle_manager._battle_end_flag:
            return

        # 检查回合结束
        if len(self._game._battle_manager._order_queue) == 0:
            self._game._battle_manager.add_history("回合结束！")
            self._game._battle_manager._new_turn_flag = True

        # 检查战斗结束
        # 英雄全死了，输了
        hero_entities = self._context.get_group(
            Matcher(
                all_of=[
                    ActorComponent,
                    HeroActorFlagComponent,
                ],
            )
        ).entities
        all_heroes_dead = all(
            hero.get(AttributeCompoment).hp <= 0 for hero in hero_entities
        )
        if all_heroes_dead:
            self._game._battle_manager.add_history("战斗结束！你输了！")
            self._game._battle_manager._battle_end_flag = True
        # 怪全死了，赢了
        enemy_entities = self._context.get_group(
            Matcher(
                all_of=[
                    ActorComponent,
                    MonsterActorFlagComponent,
                ],
            )
        ).entities
        all_enemies_dead = all(
            enemy.get(AttributeCompoment).hp <= 0 for enemy in enemy_entities
        )
        if all_enemies_dead:
            self._game._battle_manager.add_history("战斗结束！你赢了！")
            self._game._battle_manager._battle_end_flag = True

        self._game._battle_manager.write_battle_history()

        # 结束就回Home，写死 TODO
        if self._game._battle_manager._battle_end_flag:
            self._game.teleport_actors_to_stage(hero_entities, "场景.营地")
