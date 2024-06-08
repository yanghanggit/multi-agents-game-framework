from entitas import Entity #type: ignore
from rpg_game import RPGGame
from loguru import logger
from auxiliary.components import (
    BroadcastActionComponent,
    SpeakActionComponent, 
    StageComponent, 
    ActorComponent, 
    AttackActionComponent, 
    PlayerComponent, 
    GoToActionComponent,
    UsePropActionComponent, 
    WhisperActionComponent,
    SearchActionComponent,
    PortalStepActionComponent,
    PerceptionActionComponent,
    StealActionComponent,
    TradeActionComponent, 
    CheckStatusActionComponent)
from auxiliary.actor_plan_and_action import ActorAction
from auxiliary.player_proxy import PlayerProxy
from abc import ABC, abstractmethod
import datetime


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

    # 为了方便，直接在这里添加消息，不然每个子类都要写一遍
    def add_human_message(self, entity: Entity, newmsg: str) -> None:
        context = self.game.extendedcontext
        context.safe_add_human_message_to_entity(entity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerLogin(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, login_actor_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.login_actor_name = login_actor_name

    def execute(self) -> None:
        context = self.game.extendedcontext
        login_name = self.login_actor_name
        myname = self.playerproxy.name
        logger.debug(f"{self.inputname}, player name: {myname}, target name: {login_name}")

        _entity = context.get_actor_entity(login_name)
        if _entity is None:
            # 扮演的角色，本身就不存在于这个世界
            logger.error(f"{login_name}, actor is None, login failed")
            return

        playerentity = context.get_player_entity(myname)
        if playerentity is not None:
            # 已经登陆完成
            logger.error(f"{myname}, already login")
            return
        
        playercomp: PlayerComponent = _entity.get(PlayerComponent)
        if playercomp is None:
            # 扮演的角色不是设定的玩家可控制Actor
            logger.error(f"{login_name}, actor is not player ctrl actor, login failed")
            return
        
        if playercomp.name != "" and playercomp.name != myname:
            # 已经有人控制了，但不是你
            logger.error(f"{login_name}, player already ctrl by some player {playercomp.name}, login failed")
            return
    
        _entity.replace(PlayerComponent, myname)

        #登陆的消息
        self.playerproxy.add_system_message(self.game.about_game)
        
        #打印关于游戏的信息
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.playerproxy.add_system_message(f"login: {myname}, time = {time}")

        # 初始化的Actor记忆
        memory_system = context.kick_off_memory_system
        initmemory =  memory_system.get_kick_off_memory(self.login_actor_name)
        self.playerproxy.add_actor_message(self.login_actor_name, initmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################     
class PlayerAttack(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, attack_target_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.attack_target_name = attack_target_name

    def execute(self) -> None:
        context = self.game.extendedcontext 
        attack_target_name = self.attack_target_name
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_attack: player is None")
            return

        if playerentity.has(ActorComponent):
            actor_comp: ActorComponent = playerentity.get(ActorComponent)
            action = ActorAction(actor_comp.name, AttackActionComponent.__name__, [attack_target_name])
            playerentity.add(AttackActionComponent, action)

        elif playerentity.has(StageComponent):
            stagecomp: StageComponent = playerentity.get(StageComponent)
            action = ActorAction(stagecomp.name, AttackActionComponent.__name__, [attack_target_name])
            playerentity.add(AttackActionComponent, action)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################     
class PlayerGoTo(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, target_stage_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.target_stage_name = target_stage_name

    def execute(self) -> None:
        context = self.game.extendedcontext
        target_stage_name = self.target_stage_name
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_leave: player is None")
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, GoToActionComponent.__name__, [target_stage_name])
        playerentity.add(GoToActionComponent, action)

        newmsg = f"""{{"{GoToActionComponent.__name__}": ["{target_stage_name}"]}}"""
        self.add_human_message(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################     
class PlayerPortalStep(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        super().__init__(name, game, playerproxy)

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_leave: player is None")
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        current_stage_name: str = actor_comp.current_stage
        stageentity = context.get_stage_entity(current_stage_name)
        if stageentity is None:
            logger.error(f"PortalStepActionSystem: {current_stage_name} is None")
            return

        action = ActorAction(actor_comp.name, PortalStepActionComponent.__name__, [current_stage_name])
        playerentity.add(PortalStepActionComponent, action)
        
        newmsg = f"""{{"{PortalStepActionComponent.__name__}": ["{current_stage_name}"]}}"""
        self.add_human_message(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerBroadcast(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, content: str) -> None:
        super().__init__(name, game, playerproxy)
        self.content = content

    def execute(self) -> None:
        context = self.game.extendedcontext
        content = self.content
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_broadcast: player is None")
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, BroadcastActionComponent.__name__, [content])
        playerentity.add(BroadcastActionComponent, action)
       
        newmsg = f"""{{"{BroadcastActionComponent.__name__}": ["{content}"]}}"""
        self.add_human_message(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerSpeak(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, speakcontent: str) -> None:
        super().__init__(name, game, playerproxy)
        self.speakcontent = speakcontent

    def execute(self) -> None:
        context = self.game.extendedcontext
        speakcontent = self.speakcontent
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_speak: player is None")
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, SpeakActionComponent.__name__, [speakcontent])
        playerentity.add(SpeakActionComponent, action)
        
        newmsg = f"""{{"{SpeakActionComponent.__name__}": ["{speakcontent}"]}}"""
        self.add_human_message(playerentity, newmsg)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerWhisper(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, whispercontent: str) -> None:
        super().__init__(name, game, playerproxy)
        self.whispercontent = whispercontent

    def execute(self) -> None:
        context = self.game.extendedcontext
        whispercontent = self.whispercontent
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_whisper: player is None")
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, WhisperActionComponent.__name__, [whispercontent])
        playerentity.add(WhisperActionComponent, action)

        newmemory = f"""{{"{WhisperActionComponent.__name__}": ["{whispercontent}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerSearch(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, search_target_prop_name: str) -> None:
        super().__init__(name, game, playerproxy)
        self.search_target_prop_name = search_target_prop_name

    def execute(self) -> None:
        context = self.game.extendedcontext
        search_target_prop_name = self.search_target_prop_name
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            logger.warning("debug_search: player is None")
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, SearchActionComponent.__name__, [search_target_prop_name])
        playerentity.add(SearchActionComponent, action)

        newmemory = f"""{{"{SearchActionComponent.__name__}": ["{search_target_prop_name}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerPerception(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        super().__init__(name, game, playerproxy)
        

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, PerceptionActionComponent.__name__, [actor_comp.current_stage])
        playerentity.add(PerceptionActionComponent, action)

        newmemory = f"""{{"{PerceptionActionComponent.__name__}": ["{actor_comp.current_stage}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerSteal(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, command: str) -> None:
        super().__init__(name, game, playerproxy)
        # "@要偷的人>偷他的啥东西"
        self.command = command

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, StealActionComponent.__name__, [self.command])
        playerentity.add(StealActionComponent, action)

        newmemory = f"""{{"{StealActionComponent.__name__}": ["{self.command}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerTrade(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy, command: str) -> None:
        super().__init__(name, game, playerproxy)
        # "@交易的对象>我的啥东西"
        self.command = command

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, TradeActionComponent.__name__, [self.command])
        playerentity.add(TradeActionComponent, action)

        newmemory = f"""{{"{TradeActionComponent.__name__}": ["{self.command}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerCheckStatus(PlayerCommand):

    def __init__(self, name: str, game: RPGGame, playerproxy: PlayerProxy) -> None:
        super().__init__(name, game, playerproxy)

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            return
        
        if playerentity.has(CheckStatusActionComponent):
            playerentity.remove(CheckStatusActionComponent)
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, CheckStatusActionComponent.__name__, [actor_comp.name])
        playerentity.add(CheckStatusActionComponent, action)

        newmemory = f"""{{"{CheckStatusActionComponent.__name__}": ["{actor_comp.name}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
class PlayerUseProp(PlayerCommand):
    def __init__(self, inputname: str, game: RPGGame, playerproxy: PlayerProxy, command: str) -> None:
        super().__init__(inputname, game, playerproxy)
        # "@使用道具对象>道具名"
        self.command = command

    def execute(self) -> None:
        context = self.game.extendedcontext
        playerentity = context.get_player_entity(self.playerproxy.name)
        if playerentity is None:
            return
        
        actor_comp: ActorComponent = playerentity.get(ActorComponent)
        action = ActorAction(actor_comp.name, UsePropActionComponent.__name__, [self.command])
        playerentity.add(UsePropActionComponent, action)

        newmemory = f"""{{"{UsePropActionComponent.__name__}": ["{self.command}"]}}"""
        self.add_human_message(playerentity, newmemory)
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################