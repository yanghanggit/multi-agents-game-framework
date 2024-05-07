from entitas import Entity, Matcher, ExecuteProcessor #type: ignore
from auxiliary.components import StageComponent, NPCComponent, PlayerComponent
from auxiliary.extended_context import ExtendedContext
from loguru import logger
from auxiliary.director_component import StageDirectorComponent
from auxiliary.cn_builtin_prompt import direct_stage_events_prompt, direct_npc_events_prompt
from typing import List
from auxiliary.player_proxy import PlayerProxy, get_player_proxy

class DirectorSystem(ExecuteProcessor):

    def __init__(self, context: ExtendedContext) -> None:
        self.context = context
###################################################################################################################
    def execute(self) -> None:
        logger.debug("<<<<<<<<<<<<<  DirectorSystem  >>>>>>>>>>>>>>>>>")
        self.handle()
        self.directorclear()
###################################################################################################################
    def handle(self) -> None:
        entities = self.context.get_group(Matcher(all_of=[StageComponent, StageDirectorComponent])).entities
        for entity in entities:
            self.handlestage(entity)
            self.handle_npcs_in_this_stage(entity)
###################################################################################################################   
    def directorclear(self) -> None:
        entities = self.context.get_group(Matcher(all_of=[StageComponent, StageDirectorComponent])).entities
        for entity in entities:
            directorcomp: StageDirectorComponent = entity.get(StageDirectorComponent)
            directorcomp.clear()
###################################################################################################################
    def handlestage(self, entitystage: Entity) -> None:
        assert entitystage.has(StageComponent)
        stagecomp: StageComponent = entitystage.get(StageComponent)
        directorcomp: StageDirectorComponent = entitystage.get(StageDirectorComponent)
        events2stage = directorcomp.tostage(stagecomp.name, self.context)         
        newmsg = "\n".join(events2stage)
        if len(newmsg) > 0:
            prompt = direct_stage_events_prompt(newmsg, self.context)
            logger.debug(f"{stagecomp.name} => {prompt}")
            self.context.safe_add_human_message_to_entity(entitystage, prompt)
###################################################################################################################
    def handle_npcs_in_this_stage(self, entitystage: Entity) -> None:
        assert entitystage.has(StageComponent)
        stagecomp: StageComponent = entitystage.get(StageComponent)
        allnpcsinthestage = self.context.npcs_in_this_stage(stagecomp.name)
        directorcomp: StageDirectorComponent = entitystage.get(StageDirectorComponent)
        for npcentity in allnpcsinthestage:
            npccomp: NPCComponent = npcentity.get(NPCComponent)
            events2npc = directorcomp.tonpc(npccomp.name, self.context)            
            newmsg = "\n".join(events2npc)
            if len(newmsg) > 0:
                prompt = direct_npc_events_prompt(newmsg, self.context)
                logger.debug(f"{npccomp.name} => {prompt}")
                self.context.safe_add_human_message_to_entity(npcentity, prompt)
                
                #如果是player npc就再补充这个方法，通知调用客户端
                if npcentity.has(PlayerComponent):
                    self.notify_player_proxy(npcentity, newmsg, events2npc)

###################################################################################################################
    def notify_player_proxy(self, npcentity: Entity, batchmessage: str, messages: List[str]) -> None:
        if not npcentity.has(PlayerComponent):
            return
    
        playercomp: PlayerComponent = npcentity.get(PlayerComponent)
        playername: str = playercomp.name
        playerproxy = get_player_proxy(playername)
        if playerproxy is None:
            logger.error(f"notify_player_client, 玩家代理不存在{playername}???")
            return

        #登陆的消息
        npccomp: NPCComponent = npcentity.get(NPCComponent)
        playerproxy.add_npc_message(npccomp.name, batchmessage)
###################################################################################################################
    