from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from loguru import logger
from my_format_string.agent_response_json import (
    merge,
    is_repeat,
    is_markdown_json_block,
    extract_markdown_json_block,
)


############################################################################################################
############################################################################################################
############################################################################################################
class PlanFormatJSON:

    def __init__(self, input_str: str) -> None:
        self._input: str = str(input_str)
        self._output: str = str(input_str)

    def extract_md_json_block(self) -> "PlanFormatJSON":
        if is_markdown_json_block(self._output):
            self._output = extract_markdown_json_block(self._output)
        return self

    def merge_repeat_json(self) -> "PlanFormatJSON":
        if is_repeat(self._output):
            merge_res = merge(self._output)
            if merge_res is not None:
                self._output = json.dumps(merge_res, ensure_ascii=False)
        return self

    @property
    def output(self) -> str:
        return self._output


############################################################################################################
############################################################################################################
############################################################################################################


@dataclass
class AgentAction:
    name: str
    action_name: str
    values: List[str]


class AgentPlan:

    def __init__(self, name: str, input_string: str) -> None:

        self._name: str = name
        self._input_str: str = input_string
        self._json: Dict[str, List[str]] = {}
        self._actions: List[AgentAction] = []
        self._dict: Dict[str, AgentAction] = {}

        # 处理特殊的情况, 例如出现了markdown json block与重复json的情况
        # GPT4 也有可能输出markdown json block。以防万一，我们检查一下。
        # GPT4 也有可能输出重复的json。我们合并一下。有可能上面的json block的错误也犯了，所以放到第二个步骤来做
        self.json_string = (
            PlanFormatJSON(input_string)
            .extract_md_json_block()
            .merge_repeat_json()
            .output
        )

        # 核心执行
        self.load_then_build()

    ############################################################################################################
    def load_then_build(self) -> None:
        try:
            json_data = json.loads(self.json_string)
            if not self.check_fmt(json_data):
                logger.error(f"[{self._name}] = ActorPlan, check_data_format error.")
                return

            self._json = json_data
            self.build(self._json)

        except Exception as e:
            logger.error(f"[{self._name}] = json.loads error.")
        return

    ############################################################################################################
    def build(self, json: Dict[str, List[str]]) -> None:
        for key, value in json.items():
            self._actions.append(AgentAction(self._name, key, value))
            self._dict[key] = self._actions[-1]  # 方便查找

    ############################################################################################################
    def check_fmt(self, json_data: Any) -> bool:

        if not isinstance(json_data, dict):
            # assert False, f"json_data is not dict: {json_data}"
            logger.error(f"json_data is not dict: {json_data}")
            return False

        for key, value in json_data.items():
            if not isinstance(key, str):
                return False
            if not isinstance(value, list) or not all(
                isinstance(v, str) for v in value
            ):
                return False

        return True

    ############################################################################################################
    def get_by_key(self, action_name: str) -> Optional[AgentAction]:
        return self._dict.get(action_name, None)