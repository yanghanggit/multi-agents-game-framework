from loguru import logger
from tcg_models.v_0_0_1 import (
    # ActiveSkill,
    # Buff,
    Boot,
    ActorPrototype,
    StagePrototype,
    WorldSystemPrototype,
    ActorInstance,
    StageInstance,
    WorldSystemInstance,
    ActorType,
    StageType,
    # TriggerSkill,
    # TriggerType,
)
import game.tcg_game_config
from typing import List, Final

# import copy

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
def create_test_world(game_name: str, version: str) -> Boot:

    world_boot = Boot(name=game_name, version=version)
    test_world1(world_boot)

    try:
        write_path = game.tcg_game_config.GEN_WORLD_DIR / f"{game_name}.json"
        write_path.write_text(world_boot.model_dump_json(), encoding="utf-8")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return world_boot


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
#######################################################################################################################################
#######################################################################################################################################
actor_warrior_profile: Final[
    str
] = """你自幼出生在边境的小村庄，因多年与游荡的魔物作战而学会了实用的战斗技巧。
你性格坚毅，却内心善良，为了保护家乡而加入王国军队。
战乱平息后，你选择继续游历大陆，锻炼自身武技，同时寻找能为弱小者提供帮助的机会。"""
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_warrior_appearance: Final[
    str
] = """身材修长结实，皮肤在战斗与日晒中泛着古铜色。常年锻炼使得他拥有敏捷而有力的体魄，眼神坚毅，带有淡淡的疲惫。
平时身穿简洁而坚固的皮甲，胸口纹着家乡的象征图案；背负着一柄制式长剑，剑柄处刻有王国军团的标志。"""
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_wizard_profile: Final[
    str
] = """你是精灵王国里少数天赋异禀的年轻法师之一。
你自小展现出对元素魔法的惊人理解力，却也因此时常被视为“古怪”的存在。
对魔法知识的渴求，让你离开了精灵之森，开始独自游历。
你除了想提升自己的法术造诣，也希望用力量维护世界平衡。
"""
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_wizard_appearance: Final[
    str
] = """拥有精灵特有的轻盈体态和尖尖的耳朵，浅绿色的双眼流露出灵动与好奇。
身着淡雅的法袍，上面绣有象征自然与精灵文化的藤蔓花纹；披肩的银色长发随风轻舞。
一柄雕刻精细的法杖常伴在她身边，镶嵌其上的宝石微微闪烁着神秘的光芒。"""
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_warrior = ActorPrototype(
    name="角色.战士.卡恩",
    code_name="warrior",
    system_message=_comple_actor_system_prompt(
        name="角色.战士.卡恩",
        epoch_script=EPOCH_SCRIPT,
        actor_profile=actor_warrior_profile,
        appearance=actor_warrior_appearance,
    ),
    appearance=actor_warrior_appearance,
    type=ActorType.HERO,
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_wizard = ActorPrototype(
    name="角色.法师.奥露娜",
    code_name="wizard",
    system_message=_comple_actor_system_prompt(
        name="角色.法师.奥露娜",
        epoch_script=EPOCH_SCRIPT,
        actor_profile=actor_wizard_profile,
        appearance=actor_wizard_appearance,
    ),
    appearance=actor_wizard_appearance,
    type=ActorType.HERO,
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# 角色.怪物.强壮哥布林
actor_goblin1 = ActorPrototype(
    name="角色.怪物.哥布林王",
    code_name="orcking",
    system_message=_comple_actor_system_prompt(
        name="角色.怪物.哥布林王",
        epoch_script=EPOCH_SCRIPT,
        actor_profile="你的背景：生活在偏僻郊野的地下洞穴中，时不时带领其他哥布林们一起组成劫掠大军。你最喜欢劫掠附近村子的农产品和牲畜。你十分强大并且敌视其他种族，历经无数的厮杀后成为了哥布林们的首领。\n你的性格：狡猾，狂妄，残忍，自私自利。\n你的目标：你的首要目标是生存，你的次要目标是满足自己变态的施虐心和纵欲。\n你的恐惧：没有战斗。\n你的弱点：智力低下。\n你的说话风格与语气示例：（嘲讽）哈哈哈！你们这些蠢货，居然敢闯入我的领地！你们的死期到了！；（狂妄）颤抖吧！虫子！我会把你们碾碎！；残忍）我会让你们亲眼看着自己的同伴被撕成碎片，然后再慢慢折磨你们！；（狂妄）来吧，挣扎吧！让我看看你们绝望的表情！那才是我最爱的娱乐！",
        appearance="你和其他哥布林一样有深绿色的皮肤和尖尖的耳朵。但你的体格比普通哥布林更加强壮。你的身上有很浓重的臭味。",
    ),
    appearance="身躯魁梧，肌肉如岩石般坚硬，皮肤覆盖着粗糙的灰绿色鳞片，獠牙外露，眼中闪烁着残忍的红光。浑身散发着血腥与腐臭的气息，仿佛从地狱深处爬出的噩梦。",
    type=ActorType.MONSTER,
)


#######################################################################################################################################
# 场景.洞窟
stage_dungeon_kings_room = StagePrototype(
    name="场景.哥布林巢穴王座厅",
    code_name="kings_room",
    system_message=_comple_stage_system_prompt(
        name="场景.哥布林巢穴王座厅",
        epoch_script=EPOCH_SCRIPT,
        stage_profile="你是哥布林巢穴中的王座厅。这里是哥布林大王的居所，恶臭熏天，吵闹异常。",
    ),
    type=StageType.DUNGEON,
)
#######################################################################################################################################
# 场景.密室
stage_dungeon_room = StagePrototype(
    name="场景.哥布林巢穴密室",
    code_name="cave_room",
    system_message=_comple_stage_system_prompt(
        name="场景.哥布林巢穴密室",
        epoch_script=EPOCH_SCRIPT,
        stage_profile="你是哥布林巢穴中的密室。这里是哥布林大王储存宝物的地方，狭窄阴暗。",
    ),
    type=StageType.DUNGEON,
)
#######################################################################################################################################
# 场景.营地
stage_heros_camp = StagePrototype(
    name="场景.营地",
    code_name="camp",
    system_message=_comple_stage_system_prompt(
        name="场景.营地",
        epoch_script=EPOCH_SCRIPT,
        stage_profile="你是一个建在古代城堡的遗迹之上的临时营地，遗迹四周是一片未开发的原野。营地中有帐篷，营火，仓库等设施，虽然简陋，却也足够让人稍事休息，准备下一次冒险。",
    ),
    type=StageType.HOME,
)
#######################################################################################################################################
# 战斗系统
world_system_battle_system = WorldSystemPrototype(
    name="战斗系统",
    code_name="battle_system",
    system_message=_comple_world_system_system_prompt(
        name="战斗系统",
        epoch_script=EPOCH_SCRIPT,
        world_system_profile="""你是一个战斗系统，你的职责类似于DND中的GM。
玩家角色执行的动作会以卡牌的形式给出，你需要判断这些动作的合理性和有效性，并发挥想象，以故事讲述者的语气给出精彩的描述。""",
    ),
)


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
    # active_skills: List[ActiveSkill],
    # trigger_skills: List[TriggerSkill],
    # buffs: Dict[str, int],
    # attributes: List[int],
) -> ActorInstance:

    if actor_prototype.name not in world_boot.data_base.actors:
        assert False, f"Actor {actor_prototype.name} not found in data base."

    global GUID_INDEX
    GUID_INDEX += 1
    ret = ActorInstance(
        name=name,
        prototype=actor_prototype.name,
        guid=GUID_INDEX,
        # attributes=attributes,  # 暂时不用
        kick_off_message=kick_off_message,
        # active_skills=active_skills,
        # trigger_skills=trigger_skills,
        # buffs=buffs,
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
def test_world1(world_boot: Boot) -> Boot:

    # 初始化数据
    # 世界剧本
    world_boot.epoch_script = EPOCH_SCRIPT

    # 构建基础角色数据
    _initialize_data_base(
        world_boot,
        EPOCH_SCRIPT,
        [actor_warrior, actor_goblin1, actor_wizard],
        # [stage_dungeon_kings_room, stage_heros_camp, stage_dungeon_room],
        [stage_heros_camp, stage_dungeon_room],
        [world_system_battle_system],
    )

    # 创建实例：角色.战士.凯尔
    actor_warrior_instance = _create_actor_instance(
        world_boot=world_boot,
        name=actor_warrior.name,
        actor_prototype=actor_warrior,
        kick_off_message=f"""你接到了剿灭怪物的委托，和最近认识不久的队友 {actor_wizard.name} 组队扎营，准备开始冒险。""",
        # active_skills=[
        #     ActiveSkill(
        #         name="斩击",
        #         description="用剑斩向目标，造成物理伤害，力量越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3],
        #         buff=None,
        #     ),
        #     ActiveSkill(
        #         name="战地治疗",
        #         description="利用你的急救知识治疗目标的伤口，恢复生命值，智力越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3],
        #         buff=None,
        #     ),
        # ],
        # trigger_skills=[
        #     TriggerSkill(
        #         name="挺身格挡",
        #         description="挺身而出抵挡攻击，为目标添加护盾buff。",
        #         values=[2.0],
        #         buff=Buff(
        #             name="护盾",
        #             description="抵挡大量物理伤害",
        #             timing=TriggerType.ON_ATTACKED,
        #             is_debuff=False,
        #         ),
        #         timing=TriggerType.ON_ATTACKED,
        #     ),
        # ],
        # buffs={},
        # attributes=[100, 100, 1, 1, 50, 30, 20],
    )

    # 创建实例：角色.法师.露西
    actor_wizard_instance = _create_actor_instance(
        world_boot=world_boot,
        name=actor_wizard.name,
        actor_prototype=actor_wizard,
        kick_off_message=f"""你为了赚取赏金，与最近认识的队友 {actor_warrior.name} 一起组队扎营，准备开始冒险。""",
        # active_skills=[
        #     ActiveSkill(
        #         name="火球",
        #         description="默念咒文，在法杖尖端形成火球向目标发射而出，造成火焰伤害，智力越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3],
        #         buff=None,
        #     ),
        #     ActiveSkill(
        #         name="冰雾",
        #         description="默念咒文，在周围形成寒冷刺骨的冰雾，造成冰霜伤害，智力越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3],
        #         buff=None,
        #     ),
        # ],
        # trigger_skills=[
        #     TriggerSkill(
        #         name="解咒",
        #         description="使用解咒魔法移除目标身上的负面效果。",
        #         values=[1.0],
        #         buff=None,
        #         timing=TriggerType.ON_ATTACKED,
        #     )
        # ],
        # buffs={},
        # attributes=[70, 70, 1, 1, 15, 45, 60],
    )

    # 创建实例：角色.怪物.哥布林王
    actor_goblin1_instance = _create_actor_instance(
        world_boot=world_boot,
        # name=actor_goblin.name,
        name="角色.怪物.哥布林王一号",
        actor_prototype=actor_goblin1,
        kick_off_message=f"""你正于洞穴深处的王座中纵情狂欢。""",
        # active_skills=[
        #     ActiveSkill(
        #         name="猛砸",
        #         description="蓄力后猛的出拳，对目标造成物理伤害的同时眩晕目标，力量越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3, 1.0],
        #         buff=Buff(
        #             name="眩晕",
        #             description="头晕目眩，无法行动。",
        #             timing=TriggerType.ON_PLANNING,
        #             is_debuff=True,
        #         ),
        #     ),
        #     ActiveSkill(
        #         name="乱舞",
        #         description="凭借力量毫无章法的挥舞武器，对目标造成物理伤害，力量越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3],
        #         buff=None,
        #     ),
        # ],
        # trigger_skills=[
        #     TriggerSkill(
        #         name="反击",
        #         description="受到攻击后发动反击，对攻击者造成物理伤害。",
        #         values=[1.0],
        #         buff=None,
        #         timing=TriggerType.ON_ATTACKED,
        #     )
        # ],
        # buffs={
        #     "藤甲": 999,
        # },
        # attributes=[150, 150, 2, 2, 65, 40, 10],
    )

    # 创建实例：角色.怪物.哥布林王二号
    actor_goblin2_instance = _create_actor_instance(
        world_boot=world_boot,
        # name=actor_goblin2.name,
        name="角色.怪物.哥布林王二号",
        actor_prototype=actor_goblin1,
        kick_off_message=f"""你正位于洞穴深处的密室中欣赏着自己劫掠来的财宝。""",
        # active_skills=[
        #     ActiveSkill(
        #         name="猛砸",
        #         description="蓄力后猛的出拳，对目标造成物理伤害的同时眩晕目标，力量越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3, 1.0],
        #         buff=Buff(
        #             name="眩晕",
        #             description="头晕目眩，无法行动。",
        #             timing=TriggerType.ON_PLANNING,
        #             is_debuff=True,
        #         ),
        #     ),
        #     ActiveSkill(
        #         name="乱舞",
        #         description="凭借力量毫无章法的挥舞武器，对目标造成物理伤害，力量越高效果越好。",
        #         values=[0.5, 0.8, 1.0, 1.3],
        #         buff=None,
        #     ),
        # ],
        # trigger_skills=[
        #     TriggerSkill(
        #         name="反击",
        #         description="受到攻击后发动反击，对攻击者造成物理伤害。",
        #         values=[1.0],
        #         buff=None,
        #         timing=TriggerType.ON_ATTACKED,
        #     )
        # ],
        # buffs={
        #     "藤甲": 999,
        # },
        # attributes=[150, 150, 2, 2, 65, 40, 10],
    )

    # 创建实例：场景.营地，添加角色
    stage_heros_camp_instance = _create_stage_instance(
        world_boot=world_boot,
        name=stage_heros_camp.name,
        stage=stage_heros_camp,
        kick_off_message="营火静静地燃烧着。",
        actors=[actor_warrior_instance, actor_wizard_instance],
    )

    # 创建实例：场景.密室
    stage_room_instance1 = _create_stage_instance(
        world_boot=world_boot,
        name="场景.哥布林巢穴密室一号",
        stage=stage_dungeon_room,
        kick_off_message="洞穴中十分吵闹，一场战斗即将开始。",
        actors=[actor_goblin1_instance],
    )

    # 创建实例：场景.密室
    stage_room_instance2 = _create_stage_instance(
        world_boot=world_boot,
        name="场景.哥布林巢穴密室二号",
        stage=stage_dungeon_room,
        kick_off_message="哥布林大王藏匿的财宝闪闪发光。",
        actors=[actor_goblin2_instance],
    )

    # 创建实例：战斗系统
    world_system_battle_system_instance = _create_world_system_instance(
        world_boot,
        name=world_system_battle_system.name,
        world_system=world_system_battle_system,
        kick_off_message="你开始作为这个世界的战斗系统开始运行。",
    )

    # 链接实例
    _link_instance(
        world_boot,
        [actor_warrior_instance],
        [actor_wizard_instance],
        [
            stage_heros_camp_instance,
        ],
        [],
    )

    # world_boot.data_base.buffs["藤甲"] = Buff(
    #     name="藤甲",
    #     description="藤蔓缠绕全身，增加防御力。但很易燃。",
    #     timing=TriggerType.ON_ATTACKED,
    #     is_debuff=False,
    # )

    # world_boot.data_base.buffs["眩晕"] = Buff(
    #     name="眩晕",
    #     description="头晕目眩，无法行动。",
    #     timing=TriggerType.ON_PLANNING,
    #     is_debuff=True,
    # )

    # world_boot.data_base.buffs["护盾"] = Buff(
    #     name="护盾",
    #     description="抵挡大量物理伤害",
    #     timing=TriggerType.ON_ATTACKED,
    #     is_debuff=False,
    # )

    return world_boot
