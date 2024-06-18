import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent # 将项目根目录添加到sys.path
sys.path.append(str(root_dir))
from loguru import logger
from typing import List, Dict, Any, Optional, cast
from budding_world.gen_funcs import (proxy_prop)
from budding_world.excel_data import ExcelDataActor, ExcelDataProp, ExcelDataStage
import pandas as pd


class ExcelEditorStage:

    def __init__(self, 
                 data: Any, 
                 actor_data_base: Dict[str, ExcelDataActor], 
                 prop_data_base: Dict[str, ExcelDataProp], 
                 stage_data_base: Dict[str, ExcelDataStage]) -> None:
        
        if data["type"] not in ["Stage"]:
            assert False, f"Invalid Stage type: {data['type']}"
        #
        self._data: Any = data
        self._actor_data_base: Dict[str, ExcelDataActor] = actor_data_base
        self._prop_data_base: Dict[str, ExcelDataProp] = prop_data_base
        self._stage_data_base: Dict[str, ExcelDataStage] = stage_data_base
        self._stage_prop: List[ExcelDataProp] = []
        self._actors_in_stage: List[ExcelDataActor] = []
        #分析数据
        self.parse_stage_prop()
        self.parse_actors_in_stage()
#################################################################################################################################
    @property
    def attributes(self) -> str:
        assert self._data is not None
        return cast(str, self._data.get("attributes", ""))
################################################################################################################################
    def parse_stage_prop(self) -> None:
        data: Optional[str] = self._data.get("stage_prop", None)
        if data is None:
            return
        names = data.split(";")
        for _n in names:
            if _n in self._prop_data_base:
                self._stage_prop.append(self._prop_data_base[_n])
            else:
                logger.error(f"Invalid prop: {_n}")
################################################################################################################################
    def parse_actors_in_stage(self) -> None:
        data: Optional[str] = self._data.get("actors_in_stage", None)
        if data is None:
            return
        names = data.split(";")
        for _n in names:
            if _n in self._actor_data_base:
                self._actors_in_stage.append(self._actor_data_base[_n])
            else:
                logger.error(f"Invalid actor: {_n}")
################################################################################################################################
    @property
    def kick_off_memory(self) -> str:
        assert self._data is not None
        return cast(str, self._data.get("kick_off_memory", ""))
################################################################################################################################
    @property
    def exit_of_portal(self) -> str:
        assert self._data is not None
        return cast(str, self._data.get("exit_of_portal", ""))
################################################################################################################################
    def __str__(self) -> str:
       return f"ExcelEditorStage: {self._data['name']}"
################################################################################################################################
    def stage_props_proxy(self, props: List[ExcelDataProp]) -> List[Dict[str, str]]:
        ls: List[Dict[str, str]] = []
        for prop in props:
            _dt = proxy_prop(prop) #代理即可
            ls.append(_dt)
        return ls
################################################################################################################################
    ## 这里只做Actor引用，所以导出名字即可
    def stage_actors_proxy(self, actors: List[ExcelDataActor]) -> List[Dict[str, str]]:
        ls: List[Dict[str, str]] = []
        for _d in actors:
            _dt: Dict[str, str] = {} 
            _dt['name'] = _d._name  ## 这里只做引用，所以导出名字即可
            ls.append(_dt)
        return ls
################################################################################################################################
    def serialization(self) -> Dict[str, Any]:
        data_stage: ExcelDataStage = self._stage_data_base[self._data["name"]]

        _dt: Dict[str, Any] = {}
        _dt["name"] = data_stage._name
        _dt["codename"] = data_stage._codename
        _dt["description"] = data_stage._description
        _dt["url"] = data_stage.localhost()
        _dt["kick_off_memory"] = self.kick_off_memory
        _dt["exit_of_portal"] = self.exit_of_portal
        _dt['attributes'] = self.attributes 

        # 添加新的场景限制条件
        _dt["stage_entry_status"] = self.stage_entry_status
        _dt["stage_entry_actor_status"] = self.stage_entry_actor_status
        _dt["stage_entry_actor_props"] = self.stage_entry_actor_props
        _dt["stage_exit_status"] = self.stage_exit_status
        _dt["stage_exit_actor_status"] = self.stage_exit_actor_status
        _dt["stage_exit_actor_props"] = self.stage_exit_actor_props

        output_dict: Dict[str, Any] = {}
        output_dict["stage"] = _dt
        return output_dict
################################################################################################################################
    def proxy(self) -> Dict[str, Any]:
        data_stage: ExcelDataStage = self._stage_data_base[self._data["name"]]
        _dt: Dict[str, Any] = {}
        _dt["name"] = data_stage._name
        #
        props = self.stage_props_proxy(self._stage_prop)
        for _d in props:
            _d["count"] = "77" #todo
        _dt["props"] = props
        #
        actors = self.stage_actors_proxy(self._actors_in_stage)
        _dt["actors"] = actors
        #
        output: Dict[str, Any] = {}
        output["stage"] = _dt
        return output
################################################################################################################################
    def safe_get_string(self, key: str) -> str:
        if pd.isna(self._data[key]):
            return ""
        return cast(str, self._data[key]) 
################################################################################################################################
    @property
    def stage_entry_status(self) -> str:
        return self.safe_get_string("stage_entry_status")
################################################################################################################################
    @property
    def stage_entry_actor_status(self) -> str:
        return self.safe_get_string("stage_entry_actor_status")
################################################################################################################################
    @property
    def stage_entry_actor_props(self) -> str:
        return self.safe_get_string("stage_entry_actor_props")
################################################################################################################################
    @property
    def stage_exit_status(self) -> str:
        return self.safe_get_string("stage_exit_status")
################################################################################################################################
    @property
    def stage_exit_actor_status(self) -> str:
        return self.safe_get_string("stage_exit_actor_status")
################################################################################################################################
    @property
    def stage_exit_actor_props(self) -> str:
        return self.safe_get_string("stage_exit_actor_props")
################################################################################################################################