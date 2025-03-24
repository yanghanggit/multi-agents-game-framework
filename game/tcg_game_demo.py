from pathlib import Path
from loguru import logger
from models.v_0_0_1 import (
    Boot,
    ActorPrototype,
    StagePrototype,
    ActorType,
    StageType,
    BaseAttributes,
    WorldSystemPrototype,
)
from typing import Final, Optional
from game.tcg_game_demo_utils import (
    EPOCH_SCRIPT,
    _comple_actor_system_prompt,
    _comple_stage_system_prompt,
    _comple_world_system_system_prompt,
    _initialize_data_base,
    _create_actor_instance,
    _create_stage_instance,
    _create_world_system_instance,
    _link_instance,
)


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
你除了想提升自己的法术造诣，也希望用力量维护世界平衡。"""
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
actor_goblin_profile: Final[
    str
] = """你是哥布林部落中狡黠而略有头脑的成员。
与多数哥布林不同，你会主动与其他种族进行小规模交易，偶尔利用自己的狡诈为换取食物或装备做一些情报交换。
这让你在部落内部既受嫉妒又被依赖。你心中对更强大的怪物势力既畏惧又渴望效忠，因此常常成为阴谋势力的耳目或先锋。"""

#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_goblin_appearance: Final[
    str
] = """身材比普通哥布林略微高挑，瘦削却敏捷。
皮肤呈暗绿色，眼睛闪着黄褐色的光，透出无时无刻的警惕。鼻子小而上翘，双耳显得尖长。
破旧的皮质护肩上挂着几颗用来炫耀战绩的兽牙，腰间除了短刃还挂着一个小皮囊，内里装着经常使用的毒粉或烟雾弹。"""
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_orcs_profile: Final[
    str
] = """你是兽人部族中的一员，出生于荒野之地。
你从小就展现出强大的战斗力，长大后夺取了自己的小型战团，带领部下四处征战与掠夺。
在追求力量与战利品的道路上，你逐渐形成了狂热的好战性格，但也懂得利用最基本的谋略来维持在族群中的统治地位。"""

#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_orcs_appearance: Final[
    str
] = """身材高大如巨人，肌肉紧绷，皮肤是深灰色的粗糙质感。
额头上有一道丑陋的旧伤，横贯双眉，展现了他早年的激烈战斗痕迹。
獠牙突出，双目中燃烧着好战的欲望。
常穿着由兽皮和金属碎片拼接而成的胸甲，肩上披着大型凶兽的毛皮。
背后则挂着一柄巨大的战斧，上面沾染着深沉的铁锈与干涸的血迹。"""

#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_warrior_prototype = ActorPrototype(
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
actor_wizard_prototype = ActorPrototype(
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
actor_goblin_prototype = ActorPrototype(
    name="角色.怪物.哥布林-拉格",
    code_name="goblin_rag",
    system_message=_comple_actor_system_prompt(
        name="角色.怪物.哥布林-拉格",
        epoch_script=EPOCH_SCRIPT,
        actor_profile=actor_goblin_profile,
        appearance=actor_goblin_appearance,
    ),
    appearance=actor_goblin_appearance,
    type=ActorType.MONSTER,
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_orcs_prototype = ActorPrototype(
    name="角色.怪物.兽人-库洛斯",
    code_name="orc_kuros",
    system_message=_comple_actor_system_prompt(
        name="角色.怪物.兽人-库洛斯",
        epoch_script=EPOCH_SCRIPT,
        actor_profile=actor_orcs_profile,
        appearance=actor_orcs_appearance,
    ),
    appearance=actor_orcs_appearance,
    type=ActorType.MONSTER,
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
stage_dungeon_cave_prototype = StagePrototype(
    name="场景.洞窟",
    code_name="goblin_cave",
    system_message=_comple_stage_system_prompt(
        name="场景.洞窟",
        epoch_script=EPOCH_SCRIPT,
        stage_profile="你是一处位于山脚下的洞窟，洞穴内部昏暗潮湿，四处散发着腐烂的气味。光线昏暗，只能看到不远处的模糊轮廓。",
    ),
    type=StageType.DUNGEON,
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
stage_heros_camp_prototype = StagePrototype(
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
#######################################################################################################################################
#######################################################################################################################################
world_system_prototype = WorldSystemPrototype(
    name="系统.世界",
    code_name="world",
    system_message=_comple_world_system_system_prompt(
        name="系统.世界",
        epoch_script=EPOCH_SCRIPT,
        world_system_profile="你是战斗系统。",
    ),
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
world_system_instance = _create_world_system_instance(
    name=world_system_prototype.name,
    world_system=world_system_prototype,
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？""",
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_warrior_instance = _create_actor_instance(
    name=actor_warrior_prototype.name,
    actor_prototype=actor_warrior_prototype,
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？""",
    attributes=BaseAttributes(strength=15, dexterity=9, wisdom=6),
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_wizard_instance = _create_actor_instance(
    name=actor_wizard_prototype.name,
    actor_prototype=actor_wizard_prototype,
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？""",
    attributes=BaseAttributes(strength=4, dexterity=7, wisdom=18),
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_goblin_instance = _create_actor_instance(
    name="角色.怪物.哥布林-拉格",
    actor_prototype=actor_goblin_prototype,
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？""",
    attributes=BaseAttributes(strength=5, dexterity=12, wisdom=5),
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_orcs_instance = _create_actor_instance(
    name="角色.怪物.兽人-库洛斯",
    actor_prototype=actor_orcs_prototype,
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？""",
    attributes=BaseAttributes(strength=18, dexterity=6, wisdom=4),
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
stage_heros_camp_instance = _create_stage_instance(
    name=stage_heros_camp_prototype.name,
    stage=stage_heros_camp_prototype,
    kick_off_message="营火静静地燃烧着。据消息附近的洞窟里出现了怪物，需要冒险者前去调查。",
    actors=[],
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# 创建实例：场景.密室
stage_dungeon_cave_instance = _create_stage_instance(
    name=stage_dungeon_cave_prototype.name,
    stage=stage_dungeon_cave_prototype,
    kick_off_message="洞穴中十分吵闹。",
    actors=[],
)


#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
def _build_world(world_boot: Boot) -> Boot:

    # 构建基础角色数据
    _initialize_data_base(
        world_boot,
        EPOCH_SCRIPT,
        [
            actor_warrior_prototype,
            actor_goblin_prototype,
            actor_wizard_prototype,
            actor_orcs_prototype,
        ],
        [stage_heros_camp_prototype, stage_dungeon_cave_prototype],
        [world_system_prototype],
    )

    ############################################################
    ############################################################
    ############################################################
    # 改变一些数据，例如将角色放入场景 !!!!!!!!!

    # 测试直接打死。
    actor_goblin_instance.base_attributes.hp = 1

    # 角色放入场景
    player_actors = [
        actor_warrior_instance,
        actor_wizard_instance,
        actor_goblin_instance,
        # actor_orcs_instance,
    ]

    for actor in player_actors:
        stage_dungeon_cave_instance.actors.append(actor.name)

    ############################################################
    ############################################################
    ############################################################

    # 链接实例
    _link_instance(
        world_boot,
        [actor_warrior_instance],
        [actor_wizard_instance, actor_goblin_instance],
        [stage_dungeon_cave_instance],
        [],
    )

    return world_boot


#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
def create_then_write_demo_world(
    game_name: str, version: str, write_path: Path
) -> Optional[Boot]:

    try:
        # 创建世界
        world_boot = Boot(name=game_name, version=version)

        # 构建世界
        _build_world(world_boot)

        # 写入文件
        write_path.write_text(world_boot.model_dump_json(), encoding="utf-8")

        # 返回
        return world_boot

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

    assert False, "Should not reach here"
    return None


#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
