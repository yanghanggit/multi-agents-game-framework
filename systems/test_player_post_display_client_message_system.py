from entitas import ExecuteProcessor #type: ignore
from auxiliary.extended_context import ExtendedContext
from loguru import logger
from auxiliary.player_proxy import PlayerProxy, get_player_proxy
from auxiliary.extended_context import ExtendedContext


class TestPlayerPostDisplayClientMessageSystem(ExecuteProcessor):
    def __init__(self, context: ExtendedContext) -> None:
        self.context: ExtendedContext = context
############################################################################################################
    def execute(self) -> None:
        playername = self.context.user_ip
        playerproxy = get_player_proxy(playername)
        player_npc_entity = self.context.getplayer(playername)
        if player_npc_entity is None or playerproxy is None:
            return
        #
        self.display_player_client_messages(playerproxy, 10)
        #
        # while True:
        #     # 测试的客户端反馈
        #     usrinput = input(f"[{playername}]:回车继续")
        #     break   
############################################################################################################ 
    def display_player_client_messages(self, playerproxy: PlayerProxy, display_messages_count: int) -> None:
        clientmessages = playerproxy.clientmessages
        for message in clientmessages[-display_messages_count:]:
            tag = message[0]
            content = message[1]
            logger.error(f"{tag}=>{content}")
############################################################################################################
    
    