"""Demo actors, stages, and world for the multi-agents game framework."""

from .actor_warrior import create_actor_warrior
from .actor_wizard import create_actor_wizard
from .actor_goblin import create_actor_goblin
from .actor_orc import create_actor_orc
from .actor_spider import create_actor_spider
from .stage_heros_camp import create_demo_heros_camp
from .stage_dungeon1 import create_demo_dungeon1
from .stage_dungeon2 import create_demo_dungeon2
from .stage_dungeon3 import create_demo_dungeon3

# from .world import initialize_demo_game_world
from .campaign_setting import FANTASY_WORLD_RPG_CAMPAIGN_SETTING

__all__ = [
    # Demo actors
    "create_actor_warrior",
    "create_actor_wizard",
    "create_actor_goblin",
    "create_actor_orc",
    "create_actor_spider",
    # Demo stages
    "create_demo_heros_camp",
    "create_demo_dungeon1",
    "create_demo_dungeon2",
    "create_demo_dungeon3",
    # Demo dungeons (legacy names, same as above)
    "create_demo_dungeon1",
    "create_demo_dungeon2",
    "create_demo_dungeon3",
    # Demo world
    # "initialize_demo_game_world",
    # Campaign setting
    "FANTASY_WORLD_RPG_CAMPAIGN_SETTING",
]
