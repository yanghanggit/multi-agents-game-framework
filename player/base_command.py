from entitas import Entity  # type: ignore
from game.base_game import BaseGame
from player.player_proxy import PlayerProxy
from abc import ABC, abstractmethod
from typing import cast, List, Dict
import json


class PlayerCommand(ABC):

    def __init__(self, name: str, input_val: str) -> None:
        self._name: str = name
        self._input_val: str = input_val

    @abstractmethod
    def execute(self, game: BaseGame, player_proxy: PlayerProxy) -> None:
        pass

    def add_ai_message_as_planning(
        self, entity: Entity, human_message_content: str, game: BaseGame
    ) -> None:
        from game.rpg_game import RPGGame

        rpg_game = cast(RPGGame, game)
        rpg_game.context.agent_system.append_ai_message(
            rpg_game.context.safe_get_entity_name(entity), human_message_content
        )

    def split_command(self, input_val: str, split_str: str) -> str:
        if split_str in input_val:
            return input_val.split(split_str)[1].strip()
        return input_val

    def generate_action_message(self, action_name: str, values: List[str]) -> str:
        ret: Dict[str, List[str]] = {}
        ret[action_name] = values
        json_str = json.dumps(ret, ensure_ascii=False)
        return json_str
