from typing import override
from entitas import ExecuteProcessor #type: ignore
from my_entitas.extended_context import ExtendedContext
from loguru import logger
from player.player_proxy import (PlayerProxy, 
                                    get_player_proxy, 
                                    PLAYER_INPUT_MODE, 
                                    determine_player_input_mode)
from dev_config import TEST_TERMINAL_NAME, TEST_CLIENT_SHOW_MESSAGE_COUNT
from my_entitas.extended_context import ExtendedContext
from rpg_game.rpg_game import RPGGame 

class TerminalPlayerInterruptAndWaitSystem(ExecuteProcessor):
    def __init__(self, context: ExtendedContext, rpggame: RPGGame) -> None:
        self.context: ExtendedContext = context
        self.rpggame: RPGGame = rpggame
############################################################################################################
    @override
    def execute(self) -> None:
        # todo
        # 临时的设置，通过IP地址来判断是不是测试的客户端
        user_ips = self.rpggame.user_ips
        input_mode = determine_player_input_mode(user_ips)
        if input_mode != PLAYER_INPUT_MODE.TERMINAL:
            return
            
        #就是展示一下并点击继续，没什么用
        playerproxy = get_player_proxy(TEST_TERMINAL_NAME)
        player_entity = self.context.get_player_entity(TEST_TERMINAL_NAME)
        if player_entity is None or playerproxy is None:
            return
        
        self.display_client_messages(playerproxy, TEST_CLIENT_SHOW_MESSAGE_COUNT)
        while True:
            # 测试的客户端反馈
            input(f"[{TEST_TERMINAL_NAME}]:当前为中断等待，请任意键继续")
            break   
############################################################################################################ 
    def display_client_messages(self, playerproxy: PlayerProxy, display_messages_count: int) -> None:
        if display_messages_count <= 0:
            return
        clientmessages = playerproxy.client_messages
        for message in clientmessages[-display_messages_count:]:
            tag = message[0]
            content = message[1]
            logger.info(f"{tag}=>{content}")
############################################################################################################
    
    