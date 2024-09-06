from typing import Optional, Any, cast
from loguru import logger
from my_data.game_resource import GameResource
from rpg_game.rpg_game import RPGGame
from rpg_game.rpg_entitas_context import RPGEntitasContext
from extended_systems.file_system import FileSystem
from extended_systems.kick_off_message_system import KickOffMessageSystem
from typing import Optional
from my_agent.lang_serve_agent_system import LangServeAgentSystem
from extended_systems.code_name_component_system import CodeNameComponentSystem
from chaos_engineering.chaos_engineering_system import IChaosEngineering
from chaos_engineering.empty_engineering_system import EmptyChaosEngineeringSystem
from game_sample.game_sample_chaos_engineering_system import (
    GameSampleChaosEngineeringSystem,
)
from pathlib import Path
import json
import shutil
from enum import Enum
from rpg_game.terminal_game import TerminalGame
from rpg_game.web_game import WebGame
from extended_systems.guid_generator import GUIDGenerator


class GameClientType(Enum):
    INVALID = (0,)
    WEB = 1000
    TERMINAL = 2000


GAME_SAMPLE_RUNTIME_DIR = Path("game_sample/gen_runtimes")


#######################################################################################################################################
# 从文件中读取游戏数据
def load_game_builder_file(game_build_file_path: Path, version: str) -> Any:

    if not game_build_file_path.exists():
        logger.error("未找到存档，请检查存档是否存在。")
        return None

    try:

        content = game_build_file_path.read_text(encoding="utf-8")
        if content is None:
            assert content is not None, f"File is empty: {game_build_file_path}"
            return None

        data = json.loads(content)
        if data is None:
            logger.error(f"File {game_build_file_path} is empty.")
            return None

        version = cast(str, data["version"])
        if version != version:
            logger.error(f"游戏数据(World.json)与Builder版本不匹配，请检查。")
            return None

        return data

    except FileNotFoundError:
        logger.error(f"File not found: {game_build_file_path}")
        # assert False, f"File not found: {game_build_file_path}"

    return None


#######################################################################################################################################
### （临时的）写死创建
def create_game_builder(game_name: str, version: str) -> Optional[GameResource]:

    root_runtime_dir = GAME_SAMPLE_RUNTIME_DIR
    root_runtime_dir.mkdir(parents=True, exist_ok=True)

    game_build_file_path = root_runtime_dir / f"{game_name}.json"
    if not game_build_file_path.exists():
        logger.error("未找到存档，请检查存档是否存在。")
        return None

    game_data = load_game_builder_file(game_build_file_path, version)
    if game_data is None:
        logger.error("load_game_file 失败。")
        return None

    runtime_file_dir = root_runtime_dir / game_name
    return GameResource(game_name, game_data, runtime_file_dir)


#######################################################################################################################################
## 创建RPG Game
def _create_rpg_game_(
    game_name: str,
    chaos_engineering: Optional[IChaosEngineering],
    rpg_game_client_type: GameClientType,
) -> Optional[RPGGame]:

    # 依赖注入的特殊系统
    file_system = FileSystem(
        "FileSystem Because it involves IO operations, an independent system is more convenient."
    )
    memory_system = KickOffMessageSystem(
        "KickOffMessageSystem Because it involves IO operations, an independent system is more convenient."
    )
    agent_connect_system = LangServeAgentSystem(
        "LangServeAgentSystem Because it involves net operations, an independent system is more convenient."
    )
    code_name_component_system = CodeNameComponentSystem(
        "CodeNameComponentSystem, Build components by codename for special purposes"
    )
    guid_generator = GUIDGenerator("GUIDGenerator")

    ### 混沌工程系统
    if chaos_engineering is not None:
        chaos_engineering_system = chaos_engineering
    else:
        chaos_engineering_system = EmptyChaosEngineeringSystem("empty_chaos")

    # 创建上下文
    context = RPGEntitasContext(
        file_system,
        memory_system,
        agent_connect_system,
        code_name_component_system,
        chaos_engineering_system,
        guid_generator,
    )

    match rpg_game_client_type:
        case GameClientType.WEB:
            return WebGame(game_name, context)
        case GameClientType.TERMINAL:
            return TerminalGame(game_name, context)
        case _:
            assert False, "Not implemented."

    # assert False, "Not implemented."
    return None


#######################################################################################################################################
## 创建RPG Game + 读取数据
def create_rpg_game(
    game_name: str, version: str, rpg_game_client_type: GameClientType
) -> Optional[RPGGame]:

    game_builder = create_game_builder(game_name, version)
    if game_builder is None:
        logger.error("create_world_data_builder 失败。")
        return None

    # 创建游戏 + 专门的混沌工程系统
    chaos_engineering_system = GameSampleChaosEngineeringSystem(
        "MyChaosEngineeringSystem"
    )
    assert chaos_engineering_system is not None, "chaos_engineering_system is None."
    assert game_builder._data_base is not None, "game_builder.data_base_system is None."

    rpg_game = _create_rpg_game_(
        game_name, chaos_engineering_system, rpg_game_client_type
    )
    if rpg_game is None:
        logger.error("_create_rpg_game 失败。")
        return None

    # 执行创建游戏的所有动作
    return rpg_game.build(game_builder)


#######################################################################################################################################
### （临时的）写死创建
# todo
def test_save(game_name: str) -> None:

    copy2_path = GAME_SAMPLE_RUNTIME_DIR / f"{game_name}"
    if not copy2_path.exists():
        logger.error("未找到存档，请检查存档是否存在。")
        return None

    start_json_file = GAME_SAMPLE_RUNTIME_DIR / f"{game_name}.json"
    if not start_json_file.exists():
        logger.error("未找到存档，请检查存档是否存在。")
        return None

    # 拷贝运行时文件夹到另一个地方
    to_save_path = GAME_SAMPLE_RUNTIME_DIR / f"{game_name}_save"
    to_save_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(copy2_path, to_save_path, dirs_exist_ok=True)

    # 拷贝原始的运行文件
    target_file = to_save_path / f"{game_name}.json"
    if target_file.exists():
        target_file.unlink()
    shutil.copy(start_json_file, to_save_path / f"{game_name}.json")

    if not target_file.exists():
        logger.error(f"File not found: {target_file}")
        return None

    logger.info(f"Save to: {to_save_path}")
    txt = target_file.read_text(encoding="utf-8")
    obj = json.loads(txt)
    return None


#######################################################################################################################################
