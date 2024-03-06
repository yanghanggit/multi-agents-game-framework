from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langserve import RemoteRunnable
import sys

class World:
    def __init__(self, name):
        self.name = name
        self.stages = []

    def conncect(self, url):
        self.agent = RemoteRunnable(url)
        self.chat_history = []

    def add_stage(self, stage):
        self.stages.append(stage)

#
class Stage:

    def __init__(self, name):
        self.name = name
        self.actors = []

    def conncect(self, url):
        self.agent = RemoteRunnable(url)
        self.chat_history = []

    def add_actor(self, actor):
        self.actors.append(actor)

#
class Actor:
    def __init__(self, name):
        self.name = name

    def conncect(self, url):
        self.agent = RemoteRunnable(url)
        self.chat_history = []

#
class Player(Actor):
    def __init__(self, name):
        super().__init__(name)
        self.items = []

#
class NPC(Actor): 
    def __init__(self, name):
        super().__init__(name)

#
class Item(Actor): 
    def __init__(self, name):
        super().__init__(name)

#
def call_agent(target, prompt):
    if not hasattr(target, 'agent') or not hasattr(target, 'chat_history'):
        return None
    response = target.agent.invoke({"input": prompt, "chat_history": target.chat_history})
    target.chat_history.extend([HumanMessage(content=prompt), AIMessage(content=response['output'])])
    return response['output']

#希望这个方法仅表达talk的行为
def parse_input(input_val, split_str):
    if split_str in input_val:
        return input_val.split(split_str)[1].strip()
    return input_val

#
def player_talk_to_npc(player, npc, talk_content):
    return call_agent(npc, f"""#{player.name}对你说{talk_content}""")

#
def system_administrator_talk_to_npc(system_administrator, npc, talk_content):
    prompt = f"""
    # 这是系统消息
    ## 来自{system_administrator}                    
    ## 内容
    - {talk_content}
    """
    return call_agent(npc, prompt)

#
def actor_talk_to_actor(from_actor, to_actor, talk_content):
    prompt = f"""
    # 这是一次对话[talk]
    ## 来自{from_actor.name}                    
    ## 内容
    - {talk_content}
    """
    return call_agent(to_actor, prompt)

#
def stage_current(stage):
    prompt = f"""
    # 这是一个指令[command]
    ## 来自{stage.name}                    
    ## 步骤(不要输出)
    - 第1步：确认并理解你自身当前状态。
    - 第2步：确认并理解你的场景内所有NPC的当前状态。
    - 第3步：逻辑上理解以上信息（不要丢掉信息）。
    ## 需求
    - 完成思考步骤之后，输出文本内容。
    """
    return call_agent(stage, prompt)

#
def actor_plan(actor, stage_mem):
    prompt = f"""
    # 这是你要的做规划[plan]
    ## 来自{actor.name}                    
    ## 步骤(不要输出)
    - 第1步：理解场景{stage_mem}的状态。如果出现了你的名字（就是你），那么你就是场景的一部分。
    - 第2步：确认并理解你当前的状态与信息。
    - 第3步：思考你的计划的行动：是[talk]，[idle]其中之一。
    ## 需求
    - 完成思考步骤之后，输出[talk]或[idle]
    - 如果是[talk]，请输出你的对话内容。格式为“[talk]:xxxx”
    - 如果是[idle]，请输出你的思考或者行动的内容。格式为“[idle]:xxxx”
    """
    return call_agent(actor, prompt)
#
def main():

    #
    system_administrator = "系统管理员"

    #
    archivist = f"""
    # 游戏世界存档
    - 大陆纪元2000年1月1日，冬夜.
    - “卡斯帕·艾伦德”坐在他的“老猎人隐居的小木屋”中的壁炉旁，在沉思和回忆过往，并向壁炉中的火投入了一根木柴。
    - 他的小狗"断剑"在屋子里的一角睡觉。
    """

    loadprompt = f"""
    - 第1步，读取{archivist}.
    - 第2步：理解这些信息(尤其是和你有关的信息)
    - 第3步：根据信息更新你的最新状态与逻辑.
    """

    #load!!!!
    world_watcher = World("世界观察者")
    world_watcher.conncect("http://localhost:8004/world/")
    log = system_administrator_talk_to_npc(system_administrator, world_watcher,  loadprompt + "告诉我,你现在在做什么")
    print(f"[{world_watcher.name}]:", log)
    print("==============================================")

    #
    old_hunter = NPC("卡斯帕·艾伦德")
    old_hunter.conncect("http://localhost:8021/actor/npc/old_hunter/")
    log = system_administrator_talk_to_npc(system_administrator, old_hunter, loadprompt + "告诉我,你现在在做什么")
    print(f"[{old_hunter.name}]:", log)
    print("==============================================")

    #
    old_hunters_dog = NPC("小狗'短剑'")
    old_hunters_dog.conncect("http://localhost:8023/actor/npc/old_hunters_dog/")
    log = system_administrator_talk_to_npc(system_administrator, old_hunters_dog, loadprompt + "告诉我,你现在在做什么")
    print(f"[{old_hunters_dog.name}]:", log)
    print("==============================================")

    #
    old_hunters_cabin = Stage("老猎人隐居的小木屋")
    old_hunters_cabin.conncect("http://localhost:8022/stage/old_hunters_cabin/")
    log = system_administrator_talk_to_npc(system_administrator, old_hunters_cabin, loadprompt + "告诉我你现在，场景中正在发生的一切")
    print(f"[{old_hunters_cabin.name}]:", log)
    print("==============================================")

    #
    world_watcher.add_stage(old_hunters_cabin)
    old_hunters_cabin.add_actor(old_hunter)
    old_hunters_cabin.add_actor(old_hunters_dog)

    #
    player = Player("yang_hang")
    log = actor_talk_to_actor(player, world_watcher, f"我加入了这个世界")
    print(f"[{world_watcher.name}]:", log)
    print("==============================================")

    #
    while True:
        usr_input = input("[user input]: ")
        if "/quit" in usr_input:
            sys.exit()
        if "/cancel" in usr_input:
            continue

        elif "/ss" in usr_input:
            content = parse_input(usr_input, "/ss")
            stage_mem = stage_current(old_hunters_cabin)
            print(f"[{old_hunters_cabin.name}]:", stage_mem)
            print("==============================================")

        elif "/ff" in usr_input:
            content = parse_input(usr_input, "/ss")
            stage_mem = stage_current(old_hunters_cabin)
            print(f"[{old_hunters_cabin.name}]:", stage_mem)

            for actor in old_hunters_cabin.actors:
                # log = stage_current(actor)
                # print(f"[{actor.name}]:", log)
                plan = actor_plan(actor, stage_mem)
                print(f"[{actor.name}]:", plan)
            print("==============================================")



        elif "/1" in usr_input:
            content = parse_input(usr_input, "/1")
            print(f"[{system_administrator}]:", content)
            print(f"[{world_watcher.name}]:", system_administrator_talk_to_npc(system_administrator, world_watcher, content))
            print("==============================================")

        elif "/2" in usr_input:
            content = parse_input(usr_input, "/2")
            print(f"[{system_administrator}]:", content)
            print(f"[{old_hunter.name}]:", system_administrator_talk_to_npc(system_administrator, old_hunter, content))
        
        elif "/3" in usr_input:
            content = parse_input(usr_input, "/3")
            print(f"[{system_administrator}]:", content)
            print(f"[{old_hunters_cabin.name}]:", system_administrator_talk_to_npc(system_administrator, old_hunters_cabin, content))
        
        elif "4" in usr_input:
                content = parse_input(usr_input, "/4")
                print(f"[{system_administrator}]:", content)
                print(f"[{old_hunters_dog.name}]:", system_administrator_talk_to_npc(system_administrator, old_hunters_dog, content))


if __name__ == "__main__":
    print("==============================================")
    main()