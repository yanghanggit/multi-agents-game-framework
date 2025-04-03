from typing import Final, List, Dict, final
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.snapshot_v_0_0_1 import EntitySnapshot
from models.database_v_0_0_1 import DataBase
from models.objects_v_0_0_1 import Actor, Stage, WorldSystem
from models.dungeon_v_0_0_1 import Dungeon, Engagement

# 注意，不允许动！
SCHEMA_VERSION: Final[str] = "0.0.1"


###############################################################################################################################################
# 生成世界的根文件，就是世界的起点
@final
class Boot(BaseModel):
    name: str = ""
    epoch_script: str = ""
    stages: List[Stage] = []
    world_systems: List[WorldSystem] = []
    data_base: DataBase = DataBase()

    @property
    def actors(self) -> List[Actor]:
        return [actor for stage in self.stages for actor in stage.actors]


###############################################################################################################################################
@final
class AgentShortTermMemory(BaseModel):
    name: str = ""
    chat_history: List[SystemMessage | HumanMessage | AIMessage] = []


###############################################################################################################################################
# 生成世界的运行时文件，记录世界的状态
@final
class World(BaseModel):
    version: str = SCHEMA_VERSION
    runtime_index: int = 1000
    entities_snapshot: List[EntitySnapshot] = []
    agents_short_term_memory: Dict[str, AgentShortTermMemory] = {}
    dungeon: Dungeon = Dungeon(name="", levels=[], engagement=Engagement())
    boot: Boot = Boot()

    @property
    def data_base(self) -> DataBase:
        return self.boot.data_base

    def next_runtime_index(self) -> int:
        self.runtime_index += 1
        return self.runtime_index


###############################################################################################################################################
