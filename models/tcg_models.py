from typing import List, Dict, Any, final
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


###############################################################################################################################################
@final
class AgentShortTermMemory(BaseModel):
    name: str = ""
    chat_history: List[SystemMessage | HumanMessage | AIMessage] = []


###############################################################################################################################################
@final
class ComponentSnapshot(BaseModel):
    name: str
    data: Dict[str, Any]


###############################################################################################################################################
@final
class EntitySnapshot(BaseModel):
    name: str
    components: List[ComponentSnapshot]


###############################################################################################################################################
@final
class ActorPrototype(BaseModel):
    name: str
    code_name: str
    system_message: str
    base_form: str


###############################################################################################################################################
@final
class StagePrototype(BaseModel):
    name: str
    code_name: str
    system_message: str


###############################################################################################################################################
@final
class PropPrototype(BaseModel):
    name: str
    code_name: str
    details: str
    type: str
    appearance: str
    insight: str


###############################################################################################################################################
@final
class WorldSystemPrototype(BaseModel):
    name: str
    code_name: str
    system_message: str


###############################################################################################################################################
@final
class WorldDataBase(BaseModel):
    actors: Dict[str, ActorPrototype] = {}
    stages: Dict[str, StagePrototype] = {}
    props: Dict[str, PropPrototype] = {}
    world_systems: Dict[str, WorldSystemPrototype] = {}


###############################################################################################################################################
@final
class PropInstance(BaseModel):
    name: str
    guid: int
    count: int
    attributes: List[int]


###############################################################################################################################################
@final
class ActorInstance(BaseModel):
    name: str
    guid: int
    kick_off_message: str
    props: List[PropInstance]
    attributes: List[int]


###############################################################################################################################################
@final
class StageInstance(BaseModel):
    name: str
    guid: int
    actors: List[str]
    kick_off_message: str
    props: List[PropInstance]
    attributes: List[int]


###############################################################################################################################################
@final
class WorldSystemInstance(BaseModel):
    name: str
    guid: int
    kick_off_message: str


###############################################################################################################################################
# 生成世界的根文件，就是世界的起点
@final
class WorldRoot(BaseModel):
    name: str = ""
    version: str = ""
    epoch_script: str = ""
    players: List[ActorInstance] = []
    actors: List[ActorInstance] = []
    stages: List[StageInstance] = []
    world_systems: List[WorldSystemInstance] = []
    data_base: WorldDataBase = WorldDataBase()


###############################################################################################################################################
# 生成世界的运行时文件，记录世界的状态
@final
class WorldRuntime(BaseModel):
    root: WorldRoot = WorldRoot()
    entities_snapshot: List[EntitySnapshot] = []
    agents_short_term_memory: Dict[str, AgentShortTermMemory] = {}


###############################################################################################################################################
