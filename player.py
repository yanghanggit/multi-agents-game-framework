from actor import Actor
from rpg import RPG
#
class Player(Actor, RPG):
    def __init__(self, name: str):
        Actor.__init__(self, name)  # 显式地初始化Actor基类
        RPG.__init__(self)          # 显式地初始化RPG基类
        self.stage = None
        self.profile_character = "一个人类战士，身上的铠甲有些破旧，但是看起来很坚韧。"