from typing import List, Dict, List
from pydantic import BaseModel


class GameConfigModel(BaseModel):
    game_name: str = ""
    epoch_script: str = ""
    players: Dict[str, str] = {}


class GlobalConfigModel(BaseModel):
    game_configs: List[GameConfigModel] = []


class APIEndpointsConfigModel(BaseModel):
    LOGIN: str = ""
    CREATE: str = ""
    JOIN: str = ""
    START: str = ""
    EXIT: str = ""
    EXECUTE: str = ""
    SURVEY_STAGE_ACTION: str = ""
    STATUS_INVENTORY_CHECK_ACTION: str = ""
    FETCH_MESSAGES: str = ""
    RETRIEVE_ACTOR_ARCHIVES: str = ""
    RETRIEVE_STAGE_ARCHIVES: str = ""


class GameAgentsConfigModel(BaseModel):
    actors: List[Dict[str, str]]
    stages: List[Dict[str, str]]
    world_systems: List[Dict[str, str]]
