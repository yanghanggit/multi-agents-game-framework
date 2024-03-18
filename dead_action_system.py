
from entitas import Matcher, ExecuteProcessor, Entity
from components import (DeadActionComponent, 
                        LeaveActionComponent, 
                        TagActionComponent, 
                        DestroyComponent,
                        NPCComponent)
from extended_context import ExtendedContext
from actor_agent import ActorAgent
#from agents.tools.extract_md_content import wirte_content_into_md
from prompt_maker import gen_npc_archive_prompt, npc_memory_before_death


class DeadActionSystem(ExecuteProcessor):
    
    def __init__(self, context: ExtendedContext) -> None:
        self.context = context

    def execute(self) -> None:
        print("<<<<<<<<<<<<<  DeadActionSystem  >>>>>>>>>>>>>>>>>")
        entities:set[Entity] = self.context.get_group(Matcher(DeadActionComponent)).entities

        ##如果死的是NPC，就要保存存档
        for entity in entities:
            self.save_when_npc_dead(entity)

        #核心处理，如果死了就要处理下面的组件
        for entity in entities:
            if entity.has(LeaveActionComponent):
                entity.remove(LeaveActionComponent)
             
            if entity.has(TagActionComponent):
                entity.remove(TagActionComponent)
            
            if not entity.has(DestroyComponent):
                entity.add(DestroyComponent, "from DeadActionSystem")


    def save_when_npc_dead(self, entity: Entity) -> None:
        if entity.has(NPCComponent):
            npc_comp: NPCComponent = entity.get(NPCComponent)
            npc_agent: ActorAgent = npc_comp.agent
            # dead_prompt = "最终你被打死了."
            # npc_agent.request(dead_prompt)
            # 添加记忆
            mem_before_death = npc_memory_before_death(self.context)
            self.context.add_agent_memory(entity, mem_before_death)
            # 推理死亡，并且进行存档
            archive_prompt = gen_npc_archive_prompt(self.context)
            archive = npc_agent.request(archive_prompt)
            # print(f"{agent.name}:\n{archive}")
            #wirte_content_into_md(archive, f"/savedData/{npc_agent.name}.md")
            self.context.savearchive(archive, npc_agent.name)

        
             
            
        


    