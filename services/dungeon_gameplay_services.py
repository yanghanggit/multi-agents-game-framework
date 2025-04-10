from fastapi import APIRouter
from services.game_server_instance import GameServerInstance
from models_v_0_0_1 import (
    DungeonGamePlayRequest,
    DungeonGamePlayResponse,
    DungeonTransHomeRequest,
    DungeonTransHomeResponse,
)
from loguru import logger
from game.web_tcg_game import WebTCGGame
from game.tcg_game import TCGGameState
from tcg_game_systems.combat_draw_cards_system import CombatDrawCardsSystem
from tcg_game_systems.combat_round_system import CombatRoundSystem

###################################################################################################################################################################
dungeon_gameplay_router = APIRouter()


###################################################################################################################################################################
###################################################################################################################################################################
###################################################################################################################################################################
async def _execute_web_game(web_game: WebTCGGame) -> None:
    assert web_game.player.name != ""
    await web_game.a_execute()


###################################################################################################################################################################
###################################################################################################################################################################
###################################################################################################################################################################
@dungeon_gameplay_router.post(
    path="/dungeon/gameplay/v1/", response_model=DungeonGamePlayResponse
)
async def dungeon_gameplay(
    request_data: DungeonGamePlayRequest,
    game_server: GameServerInstance,
) -> DungeonGamePlayResponse:

    logger.info(f"/dungeon/gameplay/v1/: {request_data.model_dump_json()}")

    # 是否有房间？！！
    room_manager = game_server.room_manager
    if not room_manager.has_room(request_data.user_name):
        logger.error(
            f"dungeon_run: {request_data.user_name} has no room, please login first."
        )
        return DungeonGamePlayResponse(
            error=1001,
            message="没有登录，请先登录",
        )

    # 是否有游戏？！！
    current_room = room_manager.get_room(request_data.user_name)
    assert current_room is not None
    if current_room._game is None:
        logger.error(
            f"dungeon_run: {request_data.user_name} has no game, please login first."
        )
        return DungeonGamePlayResponse(
            error=1002,
            message="没有游戏，请先登录",
        )

    # 是否是WebTCGGame？！！
    web_game = current_room._game
    assert isinstance(web_game, WebTCGGame)
    assert web_game is not None

    # 判断游戏是否开始
    if not web_game.is_game_started:
        logger.error(
            f"dungeon_run: {request_data.user_name} game not started, please start it first."
        )
        return DungeonGamePlayResponse(
            error=1003,
            message="游戏没有开始，请先开始游戏",
        )

    # 判断游戏状态，不是DUNGEON状态不可以推进。
    if web_game.current_game_state != TCGGameState.DUNGEON:
        logger.error(
            f"dungeon_run: {request_data.user_name} game state error = {web_game.current_game_state}"
        )
        return DungeonGamePlayResponse(
            error=1004,
            message=f"{request_data.user_input} 只能在地下城状态下使用",
        )

    # 判断是否有战斗
    if len(web_game.current_engagement.combats) == 0:
        logger.error(f"len(web_game.current_engagement.combats) == 0")
        return DungeonGamePlayResponse(
            error=1005,
            message="len(web_game.current_engagement.combats) == 0",
        )

    # 处理逻辑
    match request_data.user_input.tag:

        case "dungeon_combat_kick_off":

            if not web_game.current_engagement.is_kickoff_phase:
                logger.error(f"not web_game.current_engagement.is_kickoff_phase")
                return DungeonGamePlayResponse(
                    error=1006,
                    message="not web_game.current_engagement.is_kickoff_phase",
                )

            # 清空消息。准备重新开始
            web_game.player.archive_and_clear_messages()
            # 推进一次游戏, 即可转换ONGOING状态。
            await _execute_web_game(web_game)
            # 返回！
            return DungeonGamePlayResponse(
                client_messages=web_game.player.client_messages,
                error=0,
                message="",
            )

        case "draw_cards":

            if not web_game.current_engagement.is_on_going_phase:
                logger.error(f"not web_game.current_engagement.is_on_going_phase")
                return DungeonGamePlayResponse(
                    error=1005,
                    message="not web_game.current_engagement.is_on_going_phase",
                )

            # 抽牌。
            combat_draw_cards_system = CombatDrawCardsSystem(
                web_game,
            )
            # 抓牌
            await combat_draw_cards_system.a_execute1()

            # 返回！
            # 清空消息。准备重新开始
            web_game.player.archive_and_clear_messages()
            return DungeonGamePlayResponse(
                client_messages=web_game.player.client_messages,
                error=0,
                message="",
            )

        case "new_round":

            if not web_game.current_engagement.is_on_going_phase:
                logger.error(f"not web_game.current_engagement.is_on_going_phase")
                return DungeonGamePlayResponse(
                    error=1005,
                    message="not web_game.current_engagement.is_on_going_phase",
                )

            # 获得当前最新的回合数据。
            combat_round_utils = CombatRoundSystem(
                web_game,
            )

            round = combat_round_utils.setup_round()
            assert not round.is_round_complete
            logger.info(f"新的回合开始 = {round.model_dump_json(indent=4)}")

            # 返回数据。
            web_game.player.archive_and_clear_messages()
            return DungeonGamePlayResponse(
                client_messages=web_game.player.client_messages,
                error=0,
                message=f"新的回合开始 = {round.model_dump_json()}",
            )

        case "play_cards":

            if not web_game.current_engagement.is_on_going_phase:
                logger.error(f"not web_game.current_engagement.is_on_going_phase")
                return DungeonGamePlayResponse(
                    error=1005,
                    message="not web_game.current_engagement.is_on_going_phase",
                )

            # 清空消息。准备重新开始
            web_game.player.archive_and_clear_messages()
            logger.debug(f"玩家输入 = {request_data.user_input.tag}, 准备行动......")
            if web_game.execute_play_card():
                # 执行一次！！！！！
                await _execute_web_game(web_game)

            # 返回！
            return DungeonGamePlayResponse(
                client_messages=web_game.player.client_messages,
                error=0,
                message="",
            )

        case "advance_next_dungeon":

            if not web_game.current_engagement.is_post_wait_phase:
                logger.error(f"not web_game.current_engagement.is_post_wait_phase")
                return DungeonGamePlayResponse(
                    error=1005,
                    message="not web_game.current_engagement.is_post_wait_phase",
                )

            if web_game.current_engagement.has_hero_won:
                next_level = web_game.current_dungeon.next_level()
                if next_level is None:
                    logger.info("没有下一关，你胜利了，应该返回营地！！！！")
                    return DungeonGamePlayResponse(
                        error=0,
                        message="没有下一关，你胜利了，应该返回营地！！！！",
                    )
                else:
                    web_game.advance_next_dungeon()
                    return DungeonGamePlayResponse(
                        error=0,
                        message=f"进入下一关：{next_level.name}",
                    )
            elif web_game.current_engagement.has_hero_lost:
                return DungeonGamePlayResponse(
                    error=0,
                    message="你已经失败了，不能继续进行游戏",
                )
        case _:
            logger.error(f"未知的请求类型 = {request_data.user_input.tag}, 不能处理！")
            assert False, f"未知的请求类型 = {request_data.user_input.tag}, 不能处理！"

    # 如果没有匹配到任何的请求类型，就返回错误。
    return DungeonGamePlayResponse(
        error=1007,
        message=f"{request_data.user_input} 是错误的输入，造成无法处理的情况！",
    )


###################################################################################################################################################################
###################################################################################################################################################################
###################################################################################################################################################################


@dungeon_gameplay_router.post(
    path="/dungeon/trans_home/v1/", response_model=DungeonTransHomeResponse
)
async def dungeon_trans_home(
    request_data: DungeonTransHomeRequest,
    game_server: GameServerInstance,
) -> DungeonTransHomeResponse:

    logger.info(f"/dungeon/trans_home/v1/: {request_data.model_dump_json()}")

    # 是否有房间？！！
    room_manager = game_server.room_manager
    if not room_manager.has_room(request_data.user_name):
        logger.error(
            f"dungeon_trans_home: {request_data.user_name} has no room, please login first."
        )
        return DungeonTransHomeResponse(
            error=1001,
            message="没有登录，请先登录",
        )

    # 是否有游戏？！！
    current_room = room_manager.get_room(request_data.user_name)
    assert current_room is not None
    if current_room._game is None:
        logger.error(
            f"dungeon_trans_home: {request_data.user_name} has no game, please login first."
        )
        return DungeonTransHomeResponse(
            error=1002,
            message="没有游戏，请先登录",
        )

    # 是否是WebTCGGame？！！
    web_game = current_room._game
    assert isinstance(web_game, WebTCGGame)
    assert web_game is not None

    # 判断游戏是否开始
    if not web_game.is_game_started:
        logger.error(
            f"dungeon_trans_home: {request_data.user_name} game not started, please start it first."
        )
        return DungeonTransHomeResponse(
            error=1003,
            message="游戏没有开始，请先开始游戏",
        )

    # 判断游戏状态，不是DUNGEON状态不可以推进。
    if web_game.current_game_state != TCGGameState.DUNGEON:
        logger.error(
            f"dungeon_trans_home: {request_data.user_name} game state error = {web_game.current_game_state}"
        )
        return DungeonTransHomeResponse(
            error=1004,
            message=f"只能在地下城状态下使用",
        )

    # 判断是否有战斗
    if len(web_game.current_engagement.combats) == 0:
        logger.error(f"len(web_game.current_engagement.combats) == 0")
        return DungeonTransHomeResponse(
            error=1005,
            message="len(web_game.current_engagement.combats) == 0",
        )

    if not web_game.current_engagement.is_post_wait_phase:
        logger.error(f"not web_game.current_engagement.is_post_wait_phase:")
        return DungeonTransHomeResponse(
            error=1005,
            message="not web_game.current_engagement.is_post_wait_phase:",
        )

    # 回家
    web_game.back_home()
    return DungeonTransHomeResponse(
        error=0,
        message="回家了",
    )


###################################################################################################################################################################
###################################################################################################################################################################
###################################################################################################################################################################
