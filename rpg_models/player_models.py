from typing import List, List
from pydantic import BaseModel
from enum import StrEnum, unique
from rpg_models.event_models import BaseEvent
from rpg_models.file_models import ActorArchiveFileModel, StageArchiveFileModel


@unique
class PlayerClientMessageTag(StrEnum):
    SYSTEM = "SYSTEM"
    ACTOR = "ACTOR"
    STAGE = "STAGE"
    KICKOFF = "KICKOFF"
    TIP = "TIP"


# 玩家客户端消息
class PlayerClientMessage(BaseModel):
    tag: str
    sender: str
    index: int = 0
    agent_event: BaseEvent  # 要根部的类，其实只需要它的序列化能力，其余的不要，所以不要出现具体类型的调用！


# 玩家代理模型
class PlayerProxyModel(BaseModel):
    name: str = ""
    actor_name: str = ""
    is_player_dead: bool = False
    client_messages: List[PlayerClientMessage] = []
    stored_kickoff_messages: List[PlayerClientMessage] = []


# 看看场景内的信息
class SurveyStageModel(BaseModel):
    content: str = ""


# 看看背包的信息
class StatusInventoryCheckModel(BaseModel):
    content: str = ""


# 检索角色档案
class RetrieveActorArchivesModel(BaseModel):
    message: str = ""
    archives: List[ActorArchiveFileModel] = []


# 检索场景档案
class RetrieveStageArchivesActionModel(BaseModel):
    message: str = ""
    archives: List[StageArchiveFileModel] = []
