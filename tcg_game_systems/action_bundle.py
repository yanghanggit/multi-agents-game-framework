from dataclasses import dataclass
from entitas import Entity  # type: ignore
from typing import Final, List, Dict, Any, Optional, cast, final, FrozenSet, NamedTuple
import json
from loguru import logger
from format_string.json_format import (
    JsonFormat,
)


############################################################################################################
@dataclass
class ActionParameters:
    name: str
    action_name: str
    values: List[str]


############################################################################################################


@final
class ActionBundle:

    def __init__(self, agent_name: str, response_content: str) -> None:

        self._agent_name: Final[str] = agent_name
        self._actions: List[ActionParameters] = []
        self._raw_response_content: Final[str] = str(response_content)

        # 准备开始处理了
        if response_content != "":
            # 处理特殊的情况, 例如出现了markdown json block与重复json的情况
            # GPT4 也有可能输出markdown json block。以防万一，我们检查一下。
            # GPT4 也有可能输出重复的json。我们合并一下。有可能上面的json block的错误也犯了，所以放到第二个步骤来做
            # 按着这个处理的顺序来做，先处理json block，再处理重复的json。
            fmt_string = (
                JsonFormat(response_content)
                .strip_json_code()
                .combine_duplicate_fragments()
                .format_output
            )

            # 核心执行
            json_data = self._load_json(fmt_string)
            self._initialize_actions(json_data)

    ############################################################################################################
    @property
    def agent_name(self) -> str:
        return self._agent_name

    ############################################################################################################
    @property
    def raw_response_content(self) -> str:
        return self._raw_response_content

    ############################################################################################################
    def _load_json(self, input_str: str) -> Dict[str, List[str]]:

        try:

            load_ret = json.loads(input_str)
            if load_ret is None:
                logger.error(f"json.loads error. \n{input_str}")
                return {}

            if not self._validate_json_format(load_ret):
                logger.error(f"ActorPlan, check_data_format error. \n{input_str}")
                return {}

            return cast(Dict[str, List[str]], load_ret)

        except Exception as e:
            logger.error(f"[{self._agent_name}] = json.loads error. \n{e}")

        return {}

    ############################################################################################################
    def _initialize_actions(self, json: Dict[str, List[str]]) -> None:
        self._actions.clear()
        for key, value in json.items():
            self._actions.append(ActionParameters(self._agent_name, key, value))

    ############################################################################################################
    def _validate_json_format(self, json_data: Any) -> bool:

        if not isinstance(json_data, dict):
            logger.error(f"json_data is not dict: {json_data}")
            return False

        for str_key, list_value in json_data.items():

            # 判断key是否是字符串
            if not isinstance(str_key, str):
                return False

            # 如果value不是list，转换成list
            if not isinstance(list_value, list):
                json_data[str_key] = [list_value]
                list_value = json_data[str_key]

            for i in range(len(list_value)):
                # 如果value不是字符串，转换成字符串
                if not isinstance(list_value[i], str):
                    list_value[i] = str(list_value[i])

        return True

    ############################################################################################################
    def retrieve_action(self, action_name: str) -> Optional[ActionParameters]:
        for action in self._actions:
            if action.action_name == action_name:
                return action
        return None

    ############################################################################################################
    def _concatenate_values(self, action_name: str, symbol: str = "") -> str:
        action = self.retrieve_action(action_name)
        if action is None or len(action.values) == 0:
            return ""
        return symbol.join(action.values)

    ############################################################################################################
    def _parse_boolean(self, action_name: str) -> bool:
        action = self.retrieve_action(action_name)
        if action is None or len(action.values) == 0:
            return False
        return action.values[0].lower() == "yes" or action.values[0].lower() == "true"

    ############################################################################################################
    def _find_registered_component(
        self, class_name: str, registered_components: FrozenSet[type[NamedTuple]]
    ) -> Optional[type[NamedTuple]]:
        for component in registered_components:
            if class_name == component.__name__:
                return component
        logger.warning(f"{class_name}不在{registered_components}中")
        return None

    ############################################################################################################
    def _ensure_actions_registered(
        self,
        registered_actions: FrozenSet[type[NamedTuple]],
    ) -> bool:
        if len(self._actions) == 0:
            return False

        for action in self._actions:
            if (
                self._find_registered_component(action.action_name, registered_actions)
                is None
            ):
                logger.warning(f"action is not correct, {action}")
                return False
        return True

    ############################################################################################################
    def _assign_action_to_entity(
        self,
        entity: Entity,
        action: ActionParameters,
        registered_actions: FrozenSet[type[NamedTuple]],
    ) -> None:
        comp_class = self._find_registered_component(
            action.action_name, registered_actions
        )
        if comp_class is None:
            return
        entity.replace(comp_class, action.name, action.values)

    ############################################################################################################
    def assign_actions_to_entity(
        self,
        target_entity: Entity,
        allowed_action_types: FrozenSet[type[NamedTuple]],
    ) -> bool:

        if not self._ensure_actions_registered(allowed_action_types):
            logger.warning(f"add_actor_actions, {self.raw_response_content}")
            return False

        ## 不能停了，只能一直继续
        for action in self._actions:
            self._assign_action_to_entity(target_entity, action, allowed_action_types)

        return True

    ############################################################################################################
