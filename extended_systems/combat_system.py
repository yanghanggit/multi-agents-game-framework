from enum import IntEnum, unique
from typing import List, final


###############################################################################################################################################
@final
@unique
class CombatState(IntEnum):
    NONE = (0,)
    INIT = (1,)
    RUNNING = (2,)
    END = 3


###############################################################################################################################################
class Combat:

    def __init__(self, name: str) -> None:
        self._name = name
        self._state: CombatState = CombatState.NONE
        
    ###############################################################################################################################################
    @property
    def current_state(self) -> CombatState:
        return self._state


###############################################################################################################################################
class CombatSystem:

    def __init__(self) -> None:
        self._combats: List[Combat] = []

    ########################################################################################################################
    def new_combat(self, name: str) -> None:
        combat = Combat(name)
        combat._state = CombatState.INIT
        self._combats.append(combat)

    ########################################################################################################################
    def current_combat(self) -> Combat:
        assert len(self._combats) > 0
        return self._combats[-1]

    ########################################################################################################################
