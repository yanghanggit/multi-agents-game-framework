# from loguru import logger
from typing import Dict


############################################################################################################
############################################################################################################
############################################################################################################
"""
这个游戏是以中国三国时代为背景的角色扮演游戏，该游戏结合《三国演义》的历史基础，融合奇幻与恐怖元素。
游戏设定在一个充满战争、权谋和英雄主义的架空三国世界。


光和七年 
徐州 琅邪国 偏远山村

州.郡国.城镇

徐州.琅邪国.偏远山村


光和_百度百科 
光和（公元178年—184年）是中国东汉皇帝汉灵帝刘宏的第三个年号，时间跨度为7年。 184年，即光和七年十二月改元为中平元年。

黄巾之乱，又称黄巾起义[a]、黄巾民变，是中国历史上东汉灵帝时的大规模民变，也是中国历史上大规模的以宗教形式（太平道）组织的起义之一，开始于汉灵帝光和七年（184年），由张角、
张宝、张梁等人领导，对东汉朝廷的统治产生了巨大的冲击。汉末三国时期一干著名诸侯群雄几乎全部都有直接、
间接参与讨伐黄巾军。同时，此战亦造成各地诸侯拥兵自重，割据一方，间接促成汉朝灭亡与三国时代的开始。
"""
############################################################################################################
############################################################################################################
############################################################################################################
"""
# 现在我希望为 这个游戏设计一个 原创的人物，作为demo的测试。

## 咱们的游戏
这个游戏是以中国三国时代为背景的角色扮演游戏，该游戏结合《三国演义》的历史基础，融合奇幻与恐怖元素。
游戏设定在一个充满战争、权谋和英雄主义的架空三国世界。

## 需求描述
1. 我希望他是生活在这个世界的一个普通人。
2. 他的出场是在公元184年的徐州 琅邪国 偏远山村。那一年是黄巾起义。
3. 他登场的时候已经是一个中年人。
4. 请你帮我设计一个这样的人物。并且给他一个名字。和生平经历及性格特点。
"""
############################################################################################################
############################################################################################################
############################################################################################################


DATA_BASE: Dict[str, str] = {}
############################################################################################################
############################################################################################################
############################################################################################################
DATA_BASE[
    "陈洛"
] = """角色性别: 男
角色年龄: 30
身份：农民
出场：公元184年，徐州 琅邪国 偏远山村

### 生平经历
出生在琅邪国的山村中，以务农为生。
懂得一些中草药疗法，偶尔帮助治疗村民的常见病痛。
性格敦厚。
他早年娶妻，但妻子生育过程中因产后感染不幸去世，这件事在他心中留下了深深的阴影。

### 要求具备的外貌特征
瘦弱，因为根据游戏的背景设定在汉末乱世，农民的生活非常艰辛，他的体型应该反映出这种生活状态。"""
############################################################################################################
############################################################################################################
############################################################################################################
DATA_BASE[
    "邓茂"
] = """角色性别: 男
角色年龄: 28
身份：农民出身，黄巾起义爆发后，加入了黄巾军。
### 生平经历
出身于冀州一个普通的农民家庭，从小就饱受地主豪强的压迫。
黄巾起义爆发后，他毅然加入了太平道，成为了一名普通的信徒。
性格敏感而残忍。
其实他也不是一个真正的信徒，他只是想通过这种方式来报复那些压迫过他的人。

### 要求具备的外貌特征
因为根据游戏的背景设定在汉末乱世，他不会很魁梧，应该是精瘦的体型。而且要反应出他的残忍性格。"""
############################################################################################################
############################################################################################################
############################################################################################################
