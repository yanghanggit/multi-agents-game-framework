from loguru import logger
import datetime
from player.player_proxy import PlayerProxy
import rpg_game.rpg_game_helper
from rpg_game.rpg_game import RPGGame
from typing import Optional
from dataclasses import dataclass
import rpg_game.rpg_game_config as rpg_game_config
import shutil
from rpg_game.rpg_game_resource import RPGGameResource
from my_models.models_def import PlayerProxyModel


@dataclass
class TerminalRunOption:
    login_player_name: str
    default_game_name: str
    check_game_resource_version: str
    show_client_message_count: int = 20
    new_game: bool = True


async def terminal_run(option: TerminalRunOption) -> None:

    # 输入要进入的世界名称
    game_name = input(
        f"请输入要进入的世界名称(必须与自动化创建的名字一致), 默认为 {option.default_game_name}:"
    )

    # 如果没有输入就用默认的
    if game_name == "":
        game_name = option.default_game_name

    # 创建游戏运行时目录，每一次运行都会删除
    game_runtime_dir = rpg_game_config.GAMES_RUNTIME_DIR / game_name
    if game_runtime_dir.exists():
        logger.warning(f"删除文件夹：{game_runtime_dir}, 这是为了测试，后续得改！！！")
        shutil.rmtree(game_runtime_dir)

    game_runtime_dir.mkdir(parents=True, exist_ok=True)
    assert game_runtime_dir.exists()

    # 根据创建还是载入进行不同的处理
    game_resource: Optional[RPGGameResource] = None
    if option.new_game:
        game_resource_file_path = rpg_game_config.GEN_GAMES_DIR / f"{game_name}.json"

        # 如果找不到游戏资源文件就退出
        if not game_resource_file_path.exists():
            logger.error(f"找不到游戏资源文件 = {game_resource_file_path}")
            return

        # 创建游戏资源
        game_resource = rpg_game.rpg_game_helper.create_game_resource(
            game_resource_file_path,
            game_runtime_dir,
            option.check_game_resource_version,
        )

        # 游戏资源可以被创建，则将game_resource_file_path这个文件拷贝一份到root_runtime_dir下
        shutil.copy(
            game_resource_file_path, game_runtime_dir / game_resource_file_path.name
        )

    else:
        # 测试用的load!!!!!!!!!!!!!!!!
        load_archive_zip_path = rpg_game_config.GAMES_ARCHIVE_DIR / f"{game_name}.zip"
        if load_archive_zip_path.exists():
            game_resource = rpg_game.rpg_game_helper.load_game_resource(
                load_archive_zip_path,
                game_runtime_dir,
                option.check_game_resource_version,
            )

    # 如果创建game_resource失败就退出
    if game_resource is None:
        logger.error(f"create_terminal_rpg_game 创建失败。")
        return

    # 创建游戏
    new_game = rpg_game.rpg_game_helper.create_terminal_rpg_game(game_resource)
    if new_game is None:
        logger.error(f"create_rpg_game 失败 = {game_name}")
        return

    # 模拟一个客户端
    player_proxy: Optional[PlayerProxy] = None
    if option.new_game:
        # 是否是控制actor游戏
        player_actor_name = terminal_player_input_select_actor(new_game)
        if player_actor_name != "":
            logger.info(f"{option.login_player_name}:{game_name}:{player_actor_name}")
            player_proxy = PlayerProxy(PlayerProxyModel(name=option.login_player_name))
            new_game.add_player(player_proxy)

            rpg_game.rpg_game_helper.player_play_new_game(
                new_game, player_proxy, player_actor_name
            )
        else:
            logger.info(
                "没有找到可以控制的角色，可能是game resource里没设置Player，此时就是观看。"
            )
    else:

        player_proxy = rpg_game.rpg_game_helper.player_play_again(
            new_game, option.login_player_name
        )

    # 核心循环
    while True:

        if new_game._will_exit:
            break

        # 运行一个回合
        await new_game.a_execute()

        # 如果没有客户端就继续
        if player_proxy is None:
            # 游戏的进程可以看log
            await terminal_continue(new_game)
            continue

        # 有客户端才进行控制。
        player_proxy.debug_client_messages(option.show_client_message_count)
        if player_proxy.over:
            # 如果死了就退出。
            new_game._will_exit = True
            continue

        if rpg_game.rpg_game_helper.is_player_turn(new_game, player_proxy):
            # 是你的输入回合
            await terminal_player_input(new_game, player_proxy)
        else:
            # 不是你的输入回合
            await terminal_player_wait(new_game, player_proxy)

    rpg_game.rpg_game_helper.save_game(new_game, rpg_game_config.GAMES_ARCHIVE_DIR)
    new_game.exit()
    new_game = None  # 其实是废话，习惯性写着吧


###############################################################################################################################################
def terminal_player_input_select_actor(game: RPGGame) -> str:
    all_names = rpg_game.rpg_game_helper.get_player_actor_names(game)
    if len(all_names) == 0:
        return ""

    while True:
        for index, actor_name in enumerate(all_names):
            logger.warning(f"{index+1}. {actor_name}")

        input_actor_index = input("请选择要控制的角色(输入序号):")
        if input_actor_index.isdigit():
            actor_index = int(input_actor_index)
            if actor_index > 0 and actor_index <= len(all_names):
                return all_names[actor_index - 1]
        else:
            logger.debug("输入错误，请重新输入。")

    return ""


#######################################################################################################################################
def terminal_player_input_watch(game_name: RPGGame, player_proxy: PlayerProxy) -> None:
    watch_action_model = rpg_game.rpg_game_helper.gen_player_watch_action_model(
        game_name, player_proxy
    )
    if watch_action_model is None:
        return

    while True:
        logger.info(watch_action_model.model_dump_json())
        input(f"按任意键继续")
        break


###############################################################################################################################################
async def terminal_player_input(game: RPGGame, player_proxy: PlayerProxy) -> None:

    while True:

        usr_input = input(f"[{player_proxy.name}]:")
        if usr_input == "":
            break

        if usr_input == "/quit":
            logger.info(f"玩家退出游戏 = {player_proxy.name}")
            game._will_exit = True
            break

        elif usr_input == "/watch" or usr_input == "/w":
            terminal_player_input_watch(game, player_proxy)

        elif usr_input == "/check" or usr_input == "/c":
            terminal_player_input_check(game, player_proxy)

        else:
            rpg_game.rpg_game_helper.add_player_command(game, player_proxy, usr_input)
            break


#######################################################################################################################################
def terminal_player_input_check(game_name: RPGGame, player_proxy: PlayerProxy) -> None:
    check_action_model = rpg_game.rpg_game_helper.gen_player_check_action_model(
        game_name, player_proxy
    )

    if check_action_model is None:
        return

    while True:
        logger.info(check_action_model.model_dump_json())
        input(f"按任意键继续")
        break


###############################################################################################################################################
async def terminal_player_wait(game: RPGGame, player_proxy: PlayerProxy) -> None:
    while True:
        input(
            f"不是你{player_proxy.name},{player_proxy.actor_name}的回合，按任意键继续游戏:{game._name}"
        )
        break


###############################################################################################################################################
async def terminal_continue(game: RPGGame) -> None:
    while True:
        input(f"{game._name} 游戏继续，没有玩家")
        break


###############################################################################################################################################


if __name__ == "__main__":
    import asyncio

    log_start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.add(f"logs/{log_start_time}.log", level="DEBUG")

    option = TerminalRunOption(
        login_player_name="北京柏林互动科技有限公司",
        default_game_name="World1",
        check_game_resource_version=rpg_game_config.CHECK_GAME_RESOURCE_VERSION,
        show_client_message_count=20,
    )
    asyncio.run(terminal_run(option))  # todo
