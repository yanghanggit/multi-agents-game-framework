from ..models import (
    ActorType,
    Actor,
    RPGCharacterProfile,
)
from .utils import (
    create_actor,
)
from .campaign_setting import FANTASY_WORLD_RPG_CAMPAIGN_SETTING


def create_actor_orc() -> Actor:
    """
    创建一个兽人角色实例

    Returns:
        Actor: 兽人角色实例
    """
    return create_actor(
        name="角色.怪物.兽人-库洛斯",
        character_sheet_name="orc",
        kick_off_message="",
        rpg_character_profile=RPGCharacterProfile(base_dexterity=1),
        type=ActorType.MONSTER,
        campaign_setting=FANTASY_WORLD_RPG_CAMPAIGN_SETTING,
        actor_profile="""你是兽人部族中的一员，出生于荒野之地。你从小就展现出强大的战斗力，长大后夺取了自己的小型战团，带领部下四处征战与掠夺。在追求力量与战利品的道路上，你逐渐形成了狂热的好战性格，但也懂得利用最基本的谋略来维持在族群中的统治地位。""",
        appearance="""身材高大如巨人，肌肉紧绷，皮肤是深灰色的粗糙质感。额头上有一道丑陋的旧伤，横贯双眉，展现了他早年的激烈战斗痕迹。獠牙突出，双目中燃烧着好战的欲望。常穿着由兽皮和金属碎片拼接而成的胸甲，肩上披着大型凶兽的毛皮。背后则挂着一柄巨大的战斧，上面沾染着深沉的铁锈与干涸的血迹。""",
    )
