from actor import Actor
from stage import Stage
from world import World

FIGHT: str = '/fight'
STAY: str = '/stay'
LEAVE: str = '/leave'
ALL_ACTIONS: list[str] = [FIGHT, STAY, LEAVE]

#
def check_data_format(action: any, targets: any, say: any, tags: any) -> bool:
    if not isinstance(action, list) or not all(isinstance(a, str) for a in action):
        return False
    if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
        return False
    if not isinstance(say, list) or not all(isinstance(s, str) for s in say):
        return False
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        return False
    return True

#
def check_actions_is_valid(actions: list[str], from_data: list[str]) -> bool:
    for action in actions:
        if action not in from_data:
            return False
    return True

#
def check_fight_or_stay_target_is_valid(stage: Stage, targets: list[str]) -> bool:
    all_actors = [stage] + stage.actors
    for target in targets:
        if not any(actor.name == target for actor in all_actors):
            return False
    return True

#
def check_leave2stage_is_valid(world: World, stage_name: str) -> bool:
    if not any(stage.name == stage_name for stage in world.stages):
        return False
    return True

class Action:

    ###
    def __init__(self, planer: Actor, action: list[str], targets: list[str], say: list[str], tags: list[str]):
        self.action = action
        self.targets = targets
        self.say = say
        self.tags = tags
        self.planer: Actor = planer

    ###
    def __str__(self):
        return f"{self.planer.name} =>: action: {self.action}, targets: {self.targets}, say: {self.say}, tags: {self.tags}"

        


