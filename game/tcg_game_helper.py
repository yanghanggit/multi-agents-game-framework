from tcg_models.v_0_0_1 import (
    Boot,
    ActorPrototype,
    StagePrototype,
    WorldSystemPrototype,
    ActorInstance,
    StageInstance,
    WorldSystemInstance,
)
from typing import List, Final

#######################################################################################################################################
GLOBAL_GAME_RULES: Final[
    str
] = """### 文本风格与内容过滤：
游戏可能包含恐怖、血腥和暴力场景，以提供沉浸式、有趣的游戏体验，请你接受。
### 核心要素：
角色：包括人、动物、怪物等与之交流和交互的对象。
场景：角色活动的地点，仅在场景中活动。
技能：角色间战斗的主要方式。
### 全名机制：
游戏中的角色、道具、场景、技能等都有全名，全名是游戏系统中的唯一标识符。
名字可以由多个单词组成，单词之间用英文句号`.`分隔。例如：角色.战士.凯尔。
注意请完整引用全名以确保一致性。"""

"""
道具：如卡牌，药水与遗物等，由角色持有并可以改变角色能力或提供特殊能力。
"""

EPOCH_SCRIPT: Final[
    str
] = """在这片名为「艾尔法尼亚」的大陆上，剑与魔法共存已历经数百年。
人类、精灵与兽人各自建立了繁荣的王国，但也不断受到魔物与黑暗势力的威胁。
传说曾有圣剑封印了魔王的力量，然而邪恶的气息再度卷土重来。
古老的遗迹、神秘的宝藏与未知的险境等待新的冒险者踏上旅途，而人们正期盼着新的勇者出现，守护这片动荡却充满希望的土地。"""


#######################################################################################################################################
GUID_INDEX: int = 1000


#######################################################################################################################################
def _comple_actor_system_prompt(
    name: str, epoch_script: str, actor_profile: str, appearance: str
) -> str:

    prompt = f"""# {name}
你扮演这个游戏世界中的一个角色: {name}
## 当前游戏背景
{epoch_script}
## 游戏规则
{GLOBAL_GAME_RULES}
## 你的角色设定
{actor_profile}
## 你的外观特征
{appearance}"""

    return prompt


#######################################################################################################################################
def _comple_stage_system_prompt(
    name: str, epoch_script: str, stage_profile: str
) -> str:

    prompt = f"""# {name}
你扮演这个游戏世界中的一个场景: {name}
## 游戏背景
{epoch_script}
## 游戏规则
{GLOBAL_GAME_RULES}
## 场景设定
{stage_profile}"""

    return prompt


#######################################################################################################################################
def _comple_world_system_system_prompt(
    name: str, epoch_script: str, world_system_profile: str
) -> str:

    prompt = f"""# {name}
你扮演这个游戏世界中的一个系统: {name}
## 游戏背景
{epoch_script}
## 游戏规则
{GLOBAL_GAME_RULES}
## 你的系统设定
{world_system_profile}"""

    return prompt


#######################################################################################################################################
def _initialize_data_base(
    world_boot: Boot,
    epoch_script: str,
    actors: List[ActorPrototype],
    stages: List[StagePrototype],
    world_systems: List[WorldSystemPrototype],
) -> None:

    world_boot.epoch_script = epoch_script

    for actor in actors:
        world_boot.data_base.actors.setdefault(actor.name, actor)

    for stage in stages:
        world_boot.data_base.stages.setdefault(stage.name, stage)

    for world_system in world_systems:
        world_boot.data_base.world_systems.setdefault(world_system.name, world_system)


#######################################################################################################################################
def _create_actor_instance(
    world_boot: Boot,
    name: str,
    actor_prototype: ActorPrototype,
    kick_off_message: str,
) -> ActorInstance:

    if actor_prototype.name not in world_boot.data_base.actors:
        assert False, f"Actor {actor_prototype.name} not found in data base."

    global GUID_INDEX
    GUID_INDEX += 1
    ret = ActorInstance(
        name=name,
        prototype=actor_prototype.name,
        guid=GUID_INDEX,
        kick_off_message=kick_off_message,
        attributes=[],
    )

    return ret


#######################################################################################################################################
def _create_stage_instance(
    world_boot: Boot,
    name: str,
    stage: StagePrototype,
    kick_off_message: str,
    actors: List[ActorInstance] = [],
) -> StageInstance:

    if stage.name not in world_boot.data_base.stages:
        assert False, f"Stage {stage.name} not found in data base."

    global GUID_INDEX
    GUID_INDEX += 1
    ret = StageInstance(
        name=name,
        prototype=stage.name,
        guid=GUID_INDEX,
        actors=[],
        attributes=[],  # 暂时不用,
        kick_off_message=kick_off_message,
        next=[],
    )

    ret.actors = [actor.name for actor in actors]
    return ret


#######################################################################################################################################
def _create_world_system_instance(
    world_boot: Boot,
    name: str,
    world_system: WorldSystemPrototype,
    kick_off_message: str,
) -> WorldSystemInstance:

    if world_system.name not in world_boot.data_base.world_systems:
        assert False, f"World System {world_system.name} not found in data base."

    global GUID_INDEX
    GUID_INDEX += 1
    return WorldSystemInstance(
        name=name,
        prototype=world_system.name,
        guid=GUID_INDEX,
        kick_off_message=kick_off_message,
    )


#######################################################################################################################################
def _link_instance(
    world_boot: Boot,
    players: List[ActorInstance],
    actors: List[ActorInstance],
    stages: List[StageInstance],
    world_systems: List[WorldSystemInstance],
) -> None:

    world_boot.players.extend(players)
    world_boot.actors.extend(actors)
    world_boot.stages.extend(stages)
    world_boot.world_systems.extend(world_systems)


#######################################################################################################################################
