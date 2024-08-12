from rpg_game.rpg_entitas_context import RPGEntitasContext
from abc import ABC, abstractmethod
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
### 这一步处理可以达到每个人看到的事件有不同的陈述，而不是全局唯一的陈述
class IStageDirectorEvent(ABC):
    @abstractmethod
    def to_actor(self, actorname: str, extended_context: RPGEntitasContext) -> str:
        pass

    @abstractmethod
    def to_stage(self, stagename: str, extended_context: RPGEntitasContext) -> str:
        pass
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################








