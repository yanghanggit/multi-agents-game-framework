import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
from typing import List, Any
import game_sample.utils
from enum import StrEnum, unique
import game_sample.configuration as configuration


@unique
class DataActorProperty(StrEnum):
    NAME = "name"
    CODENAME = "codename"
    ACTOR_PROFILE = "actor_profile"
    CONVERSATIONAL_STYLE = "conversational_style"
    PORT = "PORT"
    API = "API"
    RAG = "RAG"
    SYS_PROMPT_TEMPLATE = "sys_prompt_template"
    AGENTPY_TEMPLATE = "agentpy_template"
    BASE_FORM = "base_form"


############################################################################################################


class ExcelDataActor:

    def __init__(self, data: Any) -> None:
        assert data is not None
        self._data = data

        # 构建出来的数据
        self._gen_system_prompt: str = ""
        self._gen_agentpy: str = ""
        self._actor_archives: List[str] = []
        self._stage_archives: List[str] = []
        self._prop_archives: List[str] = []

    ############################################################################################################
    @property
    def name(self) -> str:
        return str(self._data[DataActorProperty.NAME])

    ############################################################################################################
    @property
    def codename(self) -> str:
        return str(self._data[DataActorProperty.CODENAME])

    ############################################################################################################
    @property
    def actor_profile(self) -> str:
        return str(self._data[DataActorProperty.ACTOR_PROFILE])

    ############################################################################################################
    @property
    def conversational_style(self) -> str:
        return str(self._data[DataActorProperty.CONVERSATIONAL_STYLE])

    ############################################################################################################
    @property
    def port(self) -> int:
        return int(self._data[DataActorProperty.PORT])

    ############################################################################################################
    @property
    def api(self) -> str:
        assert self.codename in str(
            self._data[DataActorProperty.API]
        ), f"{self.codename} not in {self._data[DataActorProperty.API]}"
        return str(self._data[DataActorProperty.API])

    ############################################################################################################
    @property
    def rag(self) -> str:
        return str(self._data[DataActorProperty.RAG])

    ############################################################################################################
    @property
    def sys_prompt_template_path(self) -> str:
        return str(self._data[DataActorProperty.SYS_PROMPT_TEMPLATE])

    ############################################################################################################
    @property
    def agentpy_template_path(self) -> str:
        return str(self._data[DataActorProperty.AGENTPY_TEMPLATE])

    ############################################################################################################
    @property
    def base_form(self) -> str:
        assert str(self._data[DataActorProperty.BASE_FORM]) != ""
        assert "#" not in str(self._data[DataActorProperty.BASE_FORM])
        return str(self._data[DataActorProperty.BASE_FORM])

    ############################################################################################################
    @property
    def localhost(self) -> str:
        return f"http://localhost:{self.port}{self.api}/"

    ############################################################################################################
    def gen_sys_prompt(self, sys_prompt_template: str) -> str:
        gen_prompt = str(sys_prompt_template)
        gen_prompt = gen_prompt.replace(
            configuration.SystemPromptReplaceSymbol.NAME, self.name
        )
        gen_prompt = gen_prompt.replace(
            configuration.SystemPromptReplaceSymbol.SYSTEM_PROMPT, self.actor_profile
        )
        gen_prompt = gen_prompt.replace(
            configuration.SystemPromptReplaceSymbol.BASE_FORM, self.base_form
        )
        gen_prompt = gen_prompt.replace(
            configuration.SystemPromptReplaceSymbol.CONVERSATIONAL_STYLE,
            self.conversational_style,
        )
        self._gen_system_prompt = gen_prompt
        return self._gen_system_prompt

    ############################################################################################################
    def gen_agentpy(self, agent_py_template: str) -> str:
        gen_py = str(agent_py_template)
        gen_py = gen_py.replace(
            configuration.AgentAppReplaceSymbol.SYSTEM_PROMPT_CONTENT,
            self._gen_system_prompt,
        )

        gen_py = gen_py.replace(
            configuration.AgentAppReplaceSymbol.RAG_CONTENT,
            game_sample.utils.read_text_file(configuration.GAME_SAMPLE_DIR / self.rag),
        )
        gen_py = gen_py.replace(
            configuration.AgentAppReplaceSymbol.PORT, str(self.port)
        )
        gen_py = gen_py.replace(configuration.AgentAppReplaceSymbol.API, self.api)
        self._gen_agentpy = gen_py
        return self._gen_agentpy

    ############################################################################################################
    def write_sys_prompt(self) -> None:
        game_sample.utils.write_text_file(
            configuration.GAME_SAMPLE_OUT_PUT_ACTOR_SYS_PROMPT_DIR,
            f"{self.codename}_sys_prompt.md",
            self._gen_system_prompt,
        )

    ############################################################################################################
    def write_agentpy(self) -> None:
        game_sample.utils.write_text_file(
            configuration.GAME_SAMPLE_OUT_PUT_AGENT_DIR,
            f"{self.codename}_agent.py",
            self._gen_agentpy,
        )

    ############################################################################################################
    def add_actor_archive(self, actor_name: str) -> bool:

        if actor_name == self.name:
            return False

        if actor_name in self._actor_archives:
            return True

        if actor_name in self.actor_profile:
            self._actor_archives.append(actor_name)
            return True

        return False

    ############################################################################################################
    def add_stage_archive(self, stage_name: str) -> bool:

        if stage_name in self._stage_archives:
            return True

        if stage_name in self.actor_profile:
            self._stage_archives.append(stage_name)
            return True

        return False

    ############################################################################################################
    def has_actor_in_archives(self, actor_name: str) -> bool:
        return actor_name in self._actor_archives

    ############################################################################################################
    def add_prop_archive(self, prop_name: str) -> bool:

        if prop_name in self._prop_archives:
            return True

        if prop_name in self.actor_profile:
            self._prop_archives.append(prop_name)
            return True

        return False

    ############################################################################################################
    def has_prop_archive(self, prop_name: str) -> bool:
        return prop_name in self._prop_archives


############################################################################################################
