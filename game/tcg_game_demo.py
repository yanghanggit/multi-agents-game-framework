from pathlib import Path
from loguru import logger
from models.v_0_0_1 import (
    Boot,
    ActorType,
    StageType,
    Stage,
    WorldSystem,
    BaseAttributes,
)
from typing import List, Optional
from game.tcg_game_demo_utils import (
    EPOCH_SCRIPT,
    create_actor,
    create_stage,
    copy_stage,
    create_world_system,
)


#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
test_world_system = create_world_system(
    name="系统.世界系统",
    kick_off_message=f"""你已苏醒，准备开始冒险。请告诉我你的职能和目标。""",
    epoch_script=EPOCH_SCRIPT,
    world_system_profile="你是一个测试的系统。用于生成魔法",
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# TODO, 故意放大maxhp了。
actor_warrior = create_actor(
    name="角色.战士.卡恩",
    prototype_name="warrior",
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？（请说出你的全名。）并告诉我你的战斗角色职能。回答简短(<100字)。""",
    attributes=BaseAttributes(strength=15 * 10, dexterity=9, wisdom=6),
    type=ActorType.HERO,
    epoch_script=EPOCH_SCRIPT,
    actor_profile="你自幼出生在边境的小村庄，因多年与游荡的魔物作战而学会了实用的战斗技巧。你性格坚毅，却内心善良，为了保护家乡而加入王国军队。战乱平息后，你选择继续游历大陆，锻炼自身武技，同时寻找能为弱小者提供帮助的机会。",
    appearance="""身材修长结实，皮肤在战斗与日晒中泛着古铜色。常年锻炼使得他拥有敏捷而有力的体魄，眼神坚毅，带有淡淡的疲惫。平时身穿简洁而坚固的皮甲，胸口纹着家乡的象征图案；背负着一柄制式长剑，剑柄处刻有王国军团的标志。""",
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# TODO, 故意放大maxhp了。
actor_wizard = create_actor(
    name="角色.法师.奥露娜",
    prototype_name="wizard",
    kick_off_message=f"""你已苏醒，准备开始冒险。告诉我你是谁？（请说出你的全名。）并告诉我你的战斗角色职能。回答简短(<100字)。""",
    attributes=BaseAttributes(strength=4 * 10, dexterity=7, wisdom=18),
    type=ActorType.HERO,
    epoch_script=EPOCH_SCRIPT,
    actor_profile="你是精灵王国里少数天赋异禀的年轻法师之一。你自小展现出对元素魔法的惊人理解力，却也因此时常被视为“古怪”的存在。对魔法知识的渴求，让你离开了精灵之森，开始独自游历。你除了想提升自己的法术造诣，也希望用力量维护世界平衡。",
    appearance="""拥有精灵特有的轻盈体态和尖尖的耳朵，浅绿色的双眼流露出灵动与好奇。身着淡雅的法袍，上面绣有象征自然与精灵文化的藤蔓花纹；披肩的银色长发随风轻舞。一柄雕刻精细的法杖常伴在她身边，镶嵌其上的宝石微微闪烁着神秘的光芒。""",
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_goblin = create_actor(
    name="角色.怪物.哥布林-拉格",
    prototype_name="goblin",
    kick_off_message="",
    attributes=BaseAttributes(strength=5, dexterity=12, wisdom=5),
    type=ActorType.MONSTER,
    epoch_script=EPOCH_SCRIPT,
    actor_profile="你是哥布林部落中狡黠而略有头脑的成员。与多数哥布林不同，你会主动与其他种族进行小规模交易，偶尔利用自己的狡诈为换取食物或装备做一些情报交换。这让你在部落内部既受嫉妒又被依赖。你心中对更强大的怪物势力既畏惧又渴望效忠，因此常常成为阴谋势力的耳目或先锋。",
    appearance="""身材比普通哥布林略微高挑，瘦削却敏捷。皮肤呈暗绿色，眼睛闪着黄褐色的光，透出无时无刻的警惕。鼻子小而上翘，双耳显得尖长。破旧的皮质护肩上挂着几颗用来炫耀战绩的兽牙，腰间除了短刃还挂着一个小皮囊，内里装着经常使用的毒粉或烟雾弹。""",
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
actor_orcs = create_actor(
    name="角色.怪物.兽人-库洛斯",
    prototype_name="orc",
    kick_off_message="",
    attributes=BaseAttributes(strength=18, dexterity=6, wisdom=4),
    type=ActorType.MONSTER,
    epoch_script=EPOCH_SCRIPT,
    actor_profile="""你是兽人部族中的一员，出生于荒野之地。你从小就展现出强大的战斗力，长大后夺取了自己的小型战团，带领部下四处征战与掠夺。在追求力量与战利品的道路上，你逐渐形成了狂热的好战性格，但也懂得利用最基本的谋略来维持在族群中的统治地位。""",
    appearance="""身材高大如巨人，肌肉紧绷，皮肤是深灰色的粗糙质感。额头上有一道丑陋的旧伤，横贯双眉，展现了他早年的激烈战斗痕迹。獠牙突出，双目中燃烧着好战的欲望。常穿着由兽皮和金属碎片拼接而成的胸甲，肩上披着大型凶兽的毛皮。背后则挂着一柄巨大的战斧，上面沾染着深沉的铁锈与干涸的血迹。""",
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
stage_heros_camp = create_stage(
    name="场景.营地",
    prototype_name="camp",
    kick_off_message="营火静静地燃烧着。据消息附近的洞窟里出现了怪物，需要冒险者前去调查。",
    epoch_script=EPOCH_SCRIPT,
    type=StageType.HOME,
    stage_profile="你是一个冒险者的临时营地，四周是一片未开发的原野。营地中有帐篷，营火，仓库等设施，虽然简陋，却也足够让人稍事休息，准备下一次冒险。",
    actors=[],
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# 创建实例：洞穴1
stage_dungeon_cave1 = create_stage(
    name="场景.洞窟之一",
    prototype_name="goblin_cave",
    kick_off_message="",
    epoch_script=EPOCH_SCRIPT,
    type=StageType.DUNGEON,
    stage_profile="你是一处位于山脚下的洞窟，洞穴内部昏暗潮湿，四处散发着腐烂的气味。光线昏暗，只能看到不远处的模糊轮廓。",
    actors=[],
)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
stage_dungeon_cave2 = copy_stage(
    name="场景.洞窟之二",
    prototype=stage_dungeon_cave1.prototype,
    kick_off_message="",
    epoch_script=EPOCH_SCRIPT,
    actors=[],
)


#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
def _build_world(world_boot: Boot) -> Boot:

    world_boot.epoch_script = EPOCH_SCRIPT
    assert world_boot.epoch_script != ""

    ############################################################
    ############################################################
    ############################################################
    # 改变一些数据，例如将角色放入场景 !!!!!!!!!
    # 测试直接打死。
    actor_goblin.base_attributes.hp = 1
    actor_orcs.base_attributes.hp = 1

    # 添加一些人物关系做润色。
    actor_warrior.kick_off_message += f"""\n注意:{actor_wizard.name} 是你的同伴。你目前只会使用防御类的技能！你讨厌黑暗法术，因为你认为它们是邪恶的。"""
    actor_wizard.kick_off_message += f"""\n注意:{actor_warrior.name} 是你的同伴。你最擅长的是闪电类的魔法，而且你还有一个不为别人知道的秘密：你深刻理解黑暗元素的力量，如果面对你最讨厌的东西——哥布林的时候你会毫不犹豫运用这种禁忌之力将其清除。"""

    # 营地中放置角色，这里是战士和法师。
    stage_heros_camp.actors = [actor_warrior, actor_wizard]

    # 第一个洞穴，放置哥布林。
    stage_dungeon_cave1.actors = [actor_goblin]

    # 第二个洞穴，放置兽人。
    stage_dungeon_cave2.actors = [actor_orcs]

    ############################################################
    ############################################################
    ############################################################

    _boot_link(
        world_boot,
        [
            stage_heros_camp,
            stage_dungeon_cave1,
            stage_dungeon_cave2,
        ],
        [],
    )

    return world_boot


#######################################################################################################################################
def _boot_link(
    boot: Boot,
    stages: List[Stage],
    world_systems: List[WorldSystem],
) -> None:

    assert boot.epoch_script != ""
    boot.stages = stages
    boot.world_systems = world_systems

    # 构建数据库。
    data_base = boot.data_base
    data_base.actors.clear()
    data_base.stages.clear()
    for stage in stages:

        if stage.prototype.name in data_base.stages:
            logger.warning(
                f"{stage.name}:{stage.prototype.name} = stage already exists in data_base.stages. is copy_stage?"
            )

        data_base.stages.setdefault(stage.prototype.name, stage.prototype)

        for actors in stage.actors:

            if actors.prototype.name in data_base.actors:
                logger.warning(
                    f"{actors.name}:{actors.prototype.name} = actor already exists in data_base.actors. is copy_actor?"
                )

            data_base.actors.setdefault(actors.prototype.name, actors.prototype)


#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
def create_then_write_demo_world(game_name: str, write_path: Path) -> Optional[Boot]:

    try:
        # 创建世界
        world_boot = Boot(name=game_name)

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
