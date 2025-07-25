from ..game.tcg_game_demo_utils import (
    CAMPAIGN_SETTING,
    create_world_system,
)


#######################################################################################################################################
#######################################################################################################################################

test_world_system = create_world_system(
    name="系统.世界系统",
    kick_off_message=f"""你已苏醒，准备开始冒险。请告诉我你的职能和目标。""",
    campaign_setting=CAMPAIGN_SETTING,
    world_system_profile="你是一个测试的系统。用于生成魔法",
)
