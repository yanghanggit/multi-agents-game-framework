from fastapi import APIRouter
from models.api_models import (
    SurveyStageRequest,
    SurveyStageResponse,
    StatusInventoryCheckRequest,
    StatusInventoryCheckResponse,
    RetrieveActorArchivesRequest,
    RetrieveActorArchivesResponse,
    RetrieveStageArchivesRequest,
    RetrieveStageArchivesResponse,
)
import game.rpg_game_utils
from services.game_server import GameServer

# from loguru import logger


game_play_api_router = APIRouter()


###############################################################################################################################################
@game_play_api_router.post(
    path="/survey_stage_action/", response_model=SurveyStageResponse
)
async def survey_stage_action(request_data: SurveyStageRequest) -> SurveyStageResponse:
    assert GameServer.Instance is not None

    room = GameServer.Instance.room_manager.get_room(request_data.user_name)
    if room is None or room.game is None:
        return SurveyStageResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=1,
            message="room is None",
        )

    # 没有客户端就不能看
    player_proxy = room.get_player()
    assert player_proxy is not None
    if player_proxy is None:
        return SurveyStageResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=1,
            message="player_proxy is None",
        )

    # 获得消息
    watch_action_model = game.rpg_game_utils.gen_player_survey_stage_model(
        room.game, player_proxy
    )

    if watch_action_model is None:
        return SurveyStageResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=2,
            message="watch_action_model is None",
        )

    # 返回观察游戏的信息
    return SurveyStageResponse(
        user_name=request_data.user_name,
        game_name=request_data.game_name,
        actor_name=request_data.actor_name,
        action_model=watch_action_model,
    )


###############################################################################################################################################
@game_play_api_router.post(
    path="/status_inventory_check_action/", response_model=StatusInventoryCheckResponse
)
async def status_inventory_check_action(
    request_data: StatusInventoryCheckRequest,
) -> StatusInventoryCheckResponse:

    assert GameServer.Instance is not None
    room_manager = GameServer.Instance.room_manager

    room = room_manager.get_room(request_data.user_name)
    if room is None or room.game is None:
        return StatusInventoryCheckResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=100,
            message="game_room._game is None",
        )

    # 没有客户端就不能看
    player_proxy = room.get_player()
    if player_proxy is None:
        return StatusInventoryCheckResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=1,
            message="player_proxy is None",
        )

    # 获得消息
    check_action_model = game.rpg_game_utils.gen_player_status_inventory_check_model(
        room.game, player_proxy
    )

    if check_action_model is None:
        return StatusInventoryCheckResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=2,
            message="check_action_model is None",
        )

    # 返回检查游戏的信息
    return StatusInventoryCheckResponse(
        user_name=request_data.user_name,
        game_name=request_data.game_name,
        actor_name=request_data.actor_name,
        action_model=check_action_model,
    )


###############################################################################################################################################
@game_play_api_router.post(
    path="/retrieve_actor_archives/", response_model=RetrieveActorArchivesResponse
)
async def retrieve_actor_archives(
    request_data: RetrieveActorArchivesRequest,
) -> RetrieveActorArchivesResponse:

    assert GameServer.Instance is not None
    room_manager = GameServer.Instance.room_manager

    room = room_manager.get_room(request_data.user_name)
    if room is None or room.game is None:
        return RetrieveActorArchivesResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=100,
            message="game_room._game is None",
        )

    # 没有客户端就不能看
    player_proxy = room.get_player()
    if player_proxy is None:
        return RetrieveActorArchivesResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=1,
            message="player_proxy is None",
        )

    # 获得消息
    retrieve_actor_archives_action_model = (
        game.rpg_game_utils.gen_player_retrieve_actor_archives_action_model(
            room.game, player_proxy
        )
    )

    if retrieve_actor_archives_action_model is None:
        return RetrieveActorArchivesResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=2,
            message="retrieve_actor_archives_action_model is None",
        )

    return RetrieveActorArchivesResponse(
        user_name=request_data.user_name,
        game_name=request_data.game_name,
        actor_name=request_data.actor_name,
        action_model=retrieve_actor_archives_action_model,
    )


###############################################################################################################################################
@game_play_api_router.post(
    path="/retrieve_stage_archives/", response_model=RetrieveStageArchivesResponse
)
async def retrieve_stage_archives(
    request_data: RetrieveStageArchivesRequest,
) -> RetrieveStageArchivesResponse:

    assert GameServer.Instance is not None
    room_manager = GameServer.Instance.room_manager

    room = room_manager.get_room(request_data.user_name)
    if room is None or room.game is None:
        return RetrieveStageArchivesResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=100,
            message="game_room._game is None",
        )

    player_proxy = room.get_player()
    if player_proxy is None:
        return RetrieveStageArchivesResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=1,
            message="player_proxy is None",
        )

    retrieve_stage_archives_action_model = (
        game.rpg_game_utils.gen_player_retrieve_stage_archives_action_model(
            room.game, player_proxy
        )
    )

    if retrieve_stage_archives_action_model is None:
        return RetrieveStageArchivesResponse(
            user_name=request_data.user_name,
            game_name=request_data.game_name,
            actor_name=request_data.actor_name,
            error=2,
            message="retrieve_stage_archives_action_model is None",
        )

    return RetrieveStageArchivesResponse(
        user_name=request_data.user_name,
        game_name=request_data.game_name,
        actor_name=request_data.actor_name,
        action_model=retrieve_stage_archives_action_model,
    )


###############################################################################################################################################