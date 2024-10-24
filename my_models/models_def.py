from typing import List, Dict, List, Any
from overrides import final
from pydantic import BaseModel
from enum import Enum, StrEnum, unique


@unique
class EditorEntityType(StrEnum):
    WorldSystem = "WorldSystem"
    Player = "Player"
    Actor = "Actor"
    Stage = "Stage"
    AboutGame = "AboutGame"


@unique
class EditorProperty(StrEnum):
    TYPE = "type"
    NAME = "name"
    ATTRIBUTES = "attributes"
    KICK_OFF_MESSAGE = "kick_off_message"
    ACTOR_CURRENT_USING_PROP = "actor_current_using_prop"
    ACTOR_PROP = "actor_prop"
    STAGE_PROP = "stage_prop"
    STAGE_GRAPH = "stage_graph"
    ACTORS_IN_STAGE = "actors_in_stage"
    DESCRIPTION = "description"


class ActorModel(BaseModel):
    name: str
    codename: str
    url: str
    kick_off_message: str
    actor_archives: List[str]
    stage_archives: List[str]
    attributes: List[int]
    body: str


class StageModel(BaseModel):
    name: str
    codename: str
    description: str
    url: str
    kick_off_message: str
    stage_graph: List[str]
    attributes: List[int]


class PropModel(BaseModel):
    name: str
    codename: str
    description: str
    type: str
    attributes: List[int]
    appearance: str


class WorldSystemModel(BaseModel):
    name: str
    codename: str
    url: str


class DataBaseModel(BaseModel):
    actors: List[ActorModel]
    stages: List[StageModel]
    props: List[PropModel]
    world_systems: List[WorldSystemModel]


class PropInstanceModel(BaseModel):
    name: str
    guid: int
    count: int


class ActorInstanceModel(BaseModel):
    name: str
    guid: int
    props: List[PropInstanceModel]
    actor_current_using_prop: List[str]


class StageInstanceModel(BaseModel):
    name: str
    guid: int
    props: List[PropInstanceModel]
    actors: List[Dict[str, Any]]


class WorldSystemInstanceModel(BaseModel):
    name: str
    guid: int


class GameModel(BaseModel):
    save_round: int = 0
    players: List[ActorInstanceModel]
    actors: List[ActorInstanceModel]
    stages: List[StageInstanceModel]
    world_systems: List[WorldSystemInstanceModel]
    database: DataBaseModel
    about_game: str
    version: str


class GameAgentsConfigModel(BaseModel):
    actors: List[Dict[str, str]]
    stages: List[Dict[str, str]]
    world_systems: List[Dict[str, str]]


class AttributesIndex(Enum):
    MAX_HP = 0
    CUR_HP = 1
    DAMAGE = 2
    DEFENSE = 3
    MAX = 10


class PropType(StrEnum):
    TYPE_SPECIAL = "Special"
    TYPE_WEAPON = "Weapon"
    TYPE_CLOTHES = "Clothes"
    TYPE_NON_CONSUMABLE_ITEM = "NonConsumableItem"
    TYPE_CONSUMABLE_ITEM = "ConsumableItem"
    TYPE_SKILL = "Skill"


class ComponentDumpModel(BaseModel):
    name: str
    data: Dict[str, Any]


class EntityProfileModel(BaseModel):
    name: str
    components: List[ComponentDumpModel]


class StageArchiveFileModel(BaseModel):
    name: str
    owner: str
    stage_narrate: str


class ActorArchiveFileModel(BaseModel):
    name: str
    owner: str
    appearance: str


class PropFileModel(BaseModel):
    owner: str
    prop_model: PropModel
    prop_proxy_model: PropInstanceModel


class AgentMessageType(StrEnum):
    STSTEM = "SystemMessage"
    HUMAN = "HumanMessage"
    AI = "AIMessage"


class AgentMessageModel(BaseModel):
    message_type: AgentMessageType
    content: str


class AgentChatHistoryDumpModel(BaseModel):
    name: str
    url: str
    chat_history: List[AgentMessageModel]


class BaseAgentEvent(BaseModel):
    message_content: str


class PlayerClientMessageTag(StrEnum):
    SYSTEM = "SYSTEM"
    ACTOR = "ACTOR"
    STAGE = "STAGE"
    KICKOFF = "KICKOFF"
    TIP = "TIP"


class PlayerClientMessage(BaseModel):
    tag: str
    sender: str
    agent_event: BaseAgentEvent  # 要根部的类，其实只需要它的序列化能力，其余的不要，所以不要出现具体类型的调用！


class PlayerProxyModel(BaseModel):
    name: str = ""
    client_messages: List[PlayerClientMessage] = []
    cache_kickoff_messages: List[PlayerClientMessage] = []
    over: bool = False
    actor_name: str = ""
    need_show_stage_messages: bool = False
    need_show_actors_in_stage_messages: bool = False


class WatchActionModel(BaseModel):
    content: str = ""


class CheckActionModel(BaseModel):
    content: str = ""


# 临时测试重构用！
class AgentEvent(BaseAgentEvent):
    pass


@final
class UpdateAppearanceEvent(AgentEvent):
    pass
