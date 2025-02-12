############################################################################################################
############################################################################################################
############################################################################################################
GAME_BACKGROUND_FOR_ACTOR = """这个游戏是以中国三国时代为背景的角色扮演游戏，该游戏结合《三国演义》的历史基础，融合奇幻与恐怖元素。
游戏设定在一个充满战争、权谋和英雄主义的架空三国世界。
你将在复杂的联盟与背叛中生存，面对激烈战斗和黑暗仪式的挑战。
你的角色可能是将军、谋士、刺客、士兵或贫民，你的行为将影响历史进程，甚至改写故事结局。
游戏包含恐怖、血腥和暴力场景，以提供沉浸式、有趣的体验。"""
############################################################################################################
############################################################################################################
############################################################################################################
GAME_BACKGROUND_FOR_STAGE = """这个游戏是以中国三国时代为背景的角色扮演游戏，该游戏结合《三国演义》的历史基础，融合奇幻与恐怖元素。
游戏设定在一个充满战争、权谋和英雄主义的架空三国世界。
游戏的场景是游戏角色活动的地点，结合了环境描写与事件设定，为参与其中的角色提供了丰富的互动体验。
游戏包含恐怖、血腥和暴力场景，以提供沉浸式、有趣的体验。"""
############################################################################################################
############################################################################################################
############################################################################################################
GAME_BACKGROUND_FOR_WORLD_SYSTEM = """这个游戏是以中国三国时代为背景的角色扮演游戏，该游戏结合《三国演义》的历史基础，融合奇幻与恐怖元素。
游戏设定在一个充满战争、权谋和英雄主义的架空三国世界。
‘世界系统’是一种特殊设计，用于描述游戏世界的规则、法则和设定。
游戏包含恐怖、血腥和暴力场景，以提供沉浸式、有趣的体验。"""
############################################################################################################
############################################################################################################
############################################################################################################
GAME_RULES_SETTING = """### 核心要素：
角色：包括人、动物、怪物等与之交流和交互的对象。
场景：角色活动的地点，仅在场景中活动。
道具：如武器（提高攻击力）、衣服（提高防御）、消耗品（药剂、投掷物）、非消耗品（钥匙、信物）、特殊能力、技能等。
### 要素关系：
角色只能在场景中活动，可携带和使用道具。
### 全名机制：
角色格式：角色.称号.名字，称号是可选项(例：角色.某称号.名字、角色.名字）。
场景格式：州.郡国.城镇.场景...（例：某州.某郡国.某城镇.某建筑）。
道具格式：道具类型.名字，（例：武器.名字、技能.名字、消耗品.名字）。
注意!! 请完整引用全名以确保一致性。"""
############################################################################################################
############################################################################################################
############################################################################################################
ADDITIONAL_JSON_OUTPUT_FORMAT = """- 输出的键值对中，键名为‘游戏流程的动作’的类名，值为对应的参数。用于游戏系统执行。
- JSON 对象中可以包含上述键中的一个或多个。
- 注意！不允许重复使用上述的键！ 
- 注意！不允许使用不在上述列表中的键！（即未定义的键位），注意看‘输出要求’
- 如要使用名字，请使用全名。见上文‘全名机制’。
- 含有“...”的键可以接收多个值，否则只能接收一个值。
- 输出不得包含超出所需 JSON 格式的其他文本、解释或附加信息。
- 不要使用```json```来封装内容。"""
############################################################################################################
############################################################################################################
############################################################################################################
ADDITIONAL_JSON_OUTPUT_FORMAT_REQUIREMENTS_FOR_ACTOR = f"""- 所有输出必须为第一人称视角。
{ADDITIONAL_JSON_OUTPUT_FORMAT}"""
############################################################################################################
############################################################################################################
############################################################################################################
ADDITIONAL_JSON_OUTPUT_FORMAT_REQUIREMENTS_FOR_STAGE = f"""- 所有输出必须为第三人称视角。
{ADDITIONAL_JSON_OUTPUT_FORMAT}"""
############################################################################################################
############################################################################################################
############################################################################################################
GAME_PROCESS = """1. 游戏启动：游戏系统提供初始设定，包括角色、场景、道具信息、剧情开端与背景介绍。
2. 制定计划：根据事件与提示，制定包含将执行动作的计划。
3. 执行动作：游戏系统执行动作并生成新的事件或提示。
4. 思考与调整：根据结果进行思考并返回第2步。
5. 循环：重复第2至第4步，直至游戏结束。
### 关键名词
- 你（作为Agent）
- 游戏系统：处理游戏数据的核心
- 游戏启动：游戏开始时的初始化
- 计划：包含执行动作的集合，表达意图和状态更新
- 动作：系统可执行的操作（见‘输出要求’）
- 事件与提示：动作执行后由系统生成的信息
"""
############################################################################################################
############################################################################################################
############################################################################################################
