from enum import IntEnum, StrEnum, unique


@unique
class EditorEntityType(StrEnum):
    WORLD_SYSTEM = "WorldSystem"
    PLAYER = "Player"
    ACTOR = "Actor"
    STAGE = "Stage"
    EPOCH_SCRIPT = "EpochScript"
    SPAWNER = "Spawner"
    GROUP = "Group"


@unique
class EditorProperty(StrEnum):
    NAME = "name"
    TYPE = "type"
    DESCRIPTION = "description"
    ACTOR_PROPS = "actor_props"
    ACTOR_EQUIPPED_PROPS = "actor_equipped_props"
    ACTORS_ON_STAGE = "actors_on_stage"
    GROUPS_ON_STAGE = "groups_on_stage"
    KICK_OFF_MESSAGE = "kick_off_message"
    STAGE_GRAPH = "stage_graph"
    ATTRIBUTES = "attributes"
    SPAWN_CONFIG = "spawn_config"
    SPAWNERS_ON_STAGE = "spawners_on_stage"


@unique
class GUIDType(IntEnum):
    ACTOR_TYPE = 1 * 1000 * 1000
    STAGE_TYPE = 2 * 1000 * 1000
    PROP_TYPE = 3 * 1000 * 1000
    WORLD_SYSTEM_TYPE = 4 * 1000 * 1000
    RUNTIME_ACTOR_TYPE = 5 * 1000 * 1000
    RUNTIME_PROP_TYPE = 6 * 1000 * 1000
