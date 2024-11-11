from dataclasses import dataclass
from pydantic import BaseModel
from typing import List, Optional, Final
from my_models.entity_models import GameModel
from my_models.config_models import APIEndpointsConfigModel, AllGamesConfigModel
from my_models.player_models import (
    WatchActionModel,
    CheckActionModel,
    RetrieveActorArchivesModel,
    RetrieveStageArchivesActionModel,
    PlayerClientMessage,
)


@dataclass
class WS_CONFIG:
    LOCAL_HOST: Final[str] = "127.0.0.1"
    PORT: Final[int] = 8080


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
class APIEndpointsConfigRequest(BaseModel):
    content: str = ""


class APIEndpointsConfigResponse(BaseModel):
    content: str = ""
    api_endpoints: APIEndpointsConfigModel = APIEndpointsConfigModel()
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
class LoginRequest(BaseModel):
    user_name: str = ""


class LoginResponse(BaseModel):
    user_name: str = ""
    game_config: AllGamesConfigModel = AllGamesConfigModel()
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
class CreateRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""


class CreateResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    selectable_actors: List[str] = []
    game_model: Optional[GameModel] = None
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class JoinRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class JoinResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class StartRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class StartResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    total: int = 0
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class ExitRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class ExitResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class ExecuteRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    user_input: List[str] = []


class ExecuteResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    player_input_enable: bool = False
    total: int = 0
    game_round: int = 0
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class WatchRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class WatchResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    action_model: WatchActionModel = WatchActionModel()
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class CheckRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class CheckResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    action_model: CheckActionModel = CheckActionModel()
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class FetchMessagesRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    index: int = 0
    count: int = 1


class FetchMessagesResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    messages: List[PlayerClientMessage] = []
    total: int = 0
    game_round: int = 0
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class RetrieveActorArchivesRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class RetrieveActorArchivesResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    action_model: RetrieveActorArchivesModel = RetrieveActorArchivesModel()
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


class RetrieveStageArchivesRequest(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""


class RetrieveStageArchivesResponse(BaseModel):
    user_name: str = ""
    game_name: str = ""
    actor_name: str = ""
    action_model: RetrieveStageArchivesActionModel = RetrieveStageArchivesActionModel()
    error: int = 0
    message: str = ""


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
