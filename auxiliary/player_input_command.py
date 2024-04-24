from rpg_game import RPGGame
from loguru import logger
from auxiliary.components import (
    BroadcastActionComponent, 
    SpeakActionComponent, 
    StageComponent, 
    NPCComponent, 
    FightActionComponent, 
    PlayerComponent, 
    LeaveForActionComponent, 
    WhisperActionComponent,
    SearchActionComponent,
    PrisonBreakActionComponent,
    PerceptionActionComponent,
    StealActionComponent,
    TradeActionComponent, 
    CheckStatusActionComponent)
from auxiliary.actor_action import ActorAction
from auxiliary.player_proxy import PlayerProxy
from abc import ABC, abstractmethod

####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommand(ABC):

    def __init__(self, inputname: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        self.inputname: str = inputname
        self.game: RPGGame = game
        self.playerproxy: PlayerProxy = playerproxy

    @abstractmethod
    def execute(self) -> None:
        pass
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandLogin(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, login_npc_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.login_npc_name = login_npc_name

    def execute(self) -> None:
        context = self.game.extendedcontext
        login_npc_name = self.login_npc_name
        myname = self.playerproxy.name
        logger.debug(f"{self.inputname}, player name: {myname}, target name: {login_npc_name}")

        npcentity = context.getnpc(login_npc_name)
        if npcentity is None:
            # 扮演的角色，本身就不存在于这个世界
            logger.error(f"{login_npc_name}, npc is None, login failed")
            return

        playerentity = context.getplayer(myname)
        if playerentity is not None:
            # 已经登陆完成
            logger.error(f"{myname}, already login")
            return
        
        playercomp: PlayerComponent = npcentity.get(PlayerComponent)
        if playercomp is None:
            # 扮演的角色不是设定的玩家可控制NPC
            logger.error(f"{login_npc_name}, npc is not player ctrl npc, login failed")
            return
        
        if playercomp.name != "" and playercomp.name != myname:
            # 已经有人控制了，但不是你
            logger.error(f"{login_npc_name}, player already ctrl by some player {playercomp.name}, login failed")
            return
    
        npcentity.replace(PlayerComponent, myname)
        logger.info(f"login success! {myname} => {login_npc_name}")
        
        ####
        clientmessage = self.test_client_message_after_login_success()
        logger.warning(f"{myname} 登陆了游戏, 游戏提示如下: {clientmessage}，可以开始游戏了")

    ## 登录之后，客户端需要看到的消息
    def test_client_message_after_login_success(self) -> str:
        context = self.game.extendedcontext
        memory_system = context.memory_system
        npcentity = context.getnpc(self.login_npc_name)
        assert npcentity is not None
        safename = context.safe_get_entity_name(npcentity)
        return memory_system.getmemory(safename)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################     
class PlayerCommandAttack(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, attack_target_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.attack_target_name = attack_target_name

    def execute(self) -> None:
        context = self.game.extendedcontext 
        attack_target_name = self.attack_target_name
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_attack: player is None")
            return

        if playerentity.has(NPCComponent):
            npccomp: NPCComponent = playerentity.get(NPCComponent)
            action = ActorAction(npccomp.name, FightActionComponent.__name__, [attack_target_name])
            playerentity.add(FightActionComponent, action)

        elif playerentity.has(StageComponent):
            stagecomp: StageComponent = playerentity.get(StageComponent)
            action = ActorAction(stagecomp.name, FightActionComponent.__name__, [attack_target_name])
            playerentity.add(FightActionComponent, action)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################     
class PlayerCommandLeaveFor(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, target_stage_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.target_stage_name = target_stage_name

    def execute(self) -> None:
        context = self.game.extendedcontext
        target_stage_name = self.target_stage_name
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_leave: player is None")
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, LeaveForActionComponent.__name__, [target_stage_name])
        playerentity.add(LeaveForActionComponent, action)

        newmsg = f"""{{"{LeaveForActionComponent.__name__}": ["{target_stage_name}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################     
class PlayerCommandPrisonBreak(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        super().__init__(name, game, playerproxy)

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_leave: player is None")
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        current_stage_name: str = npccomp.current_stage
        stageentity = context.getstage(current_stage_name)
        if stageentity is None:
            logger.error(f"PrisonBreakActionSystem: {current_stage_name} is None")
            return

        action = ActorAction(npccomp.name, PrisonBreakActionComponent.__name__, [current_stage_name])
        playerentity.add(LeaveForActionComponent, action)
        
        newmsg = f"""{{"{PrisonBreakActionComponent.__name__}": ["{current_stage_name}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandBroadcast(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, content: str) -> None:
        super().__init__(name, game, playerproxy)
        self.content = content

    def execute(self) -> None:
        context = self.game.extendedcontext
        content = self.content
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_broadcast: player is None")
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, BroadcastActionComponent.__name__, [content])
        playerentity.add(BroadcastActionComponent, action)
       
        newmsg = f"""{{"{BroadcastActionComponent.__name__}": ["{content}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandSpeak(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, speakcontent: str) -> None:
        super().__init__(name, game, playerproxy)
        self.speakcontent = speakcontent

    def execute(self) -> None:
        context = self.game.extendedcontext
        speakcontent = self.speakcontent
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_speak: player is None")
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, SpeakActionComponent.__name__, [speakcontent])
        playerentity.add(SpeakActionComponent, action)
        
        newmsg = f"""{{"{SpeakActionComponent.__name__}": ["{speakcontent}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandWhisper(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, whispercontent: str) -> None:
        super().__init__(name, game, playerproxy)
        self.whispercontent = whispercontent

    def execute(self) -> None:
        context = self.game.extendedcontext
        whispercontent = self.whispercontent
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_whisper: player is None")
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, WhisperActionComponent.__name__, [whispercontent])
        playerentity.add(WhisperActionComponent, action)

        newmemory = f"""{{"{WhisperActionComponent.__name__}": ["{whispercontent}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandSearch(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, search_target_prop_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.search_target_prop_name = search_target_prop_name

    def execute(self) -> None:
        context = self.game.extendedcontext
        search_target_prop_name = self.search_target_prop_name
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_search: player is None")
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, SearchActionComponent.__name__, [search_target_prop_name])
        playerentity.add(SearchActionComponent, action)

        newmemory = f"""{{"{SearchActionComponent.__name__}": ["{search_target_prop_name}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandPerception(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        super().__init__(name, game, playerproxy)
        

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, PerceptionActionComponent.__name__, [npccomp.current_stage])
        playerentity.add(PerceptionActionComponent, action)

        newmemory = f"""{{"{PerceptionActionComponent.__name__}": ["{npccomp.current_stage}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandSteal(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, command: str) -> None:
        super().__init__(name, game, playerproxy)
        # "@要偷的人>偷他的啥东西"
        self.command = command

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, StealActionComponent.__name__, [self.command])
        playerentity.add(StealActionComponent, action)

        newmemory = f"""{{"{StealActionComponent.__name__}": ["{self.command}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandTrade(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, command: str) -> None:
        super().__init__(name, game, playerproxy)
        # "@交易的对象>我的啥东西"
        self.command = command

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, TradeActionComponent.__name__, [self.command])
        playerentity.add(TradeActionComponent, action)

        newmemory = f"""{{"{TradeActionComponent.__name__}": ["{self.command}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCommandCheckStatus(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        super().__init__(name, game, playerproxy)

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.getplayer(self.playerproxy.name)
        if playerentity is None:
            return
        
        npccomp: NPCComponent = playerentity.get(NPCComponent)
        action = ActorAction(npccomp.name, CheckStatusActionComponent.__name__, [npccomp.name])
        playerentity.add(CheckStatusActionComponent, action)

        newmemory = f"""{{"{CheckStatusActionComponent.__name__}": ["{npccomp.name}"]}}"""
        context.safe_add_human_message_to_entity(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################