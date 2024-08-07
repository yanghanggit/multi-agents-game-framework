import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
import pandas as pd
from loguru import logger
from pandas.core.frame import DataFrame
from typing import Dict, Any
from game_sample.excel_data import ExcelDataActor, ExcelDataStage, ExcelDataProp, ExcelDataWorldSystem
from pathlib import Path
from game_sample.utils import read_system_prompt_md, read_agentpy_template
from game_sample.configuration import GAME_NAME

############################################################################################################
def gen_all_actors(sheet: DataFrame, output: Dict[str, ExcelDataActor]) -> None:
    ## 读取Excel文件
    for index, row in sheet.iterrows():
        if pd.isna(row["name"]):
            continue
        
        excel_actor =  ExcelDataActor(row)
        #
        system_prompt_path = Path(GAME_NAME) / excel_actor.sys_prompt_template_path
        assert system_prompt_path.exists(), f"File not found: {system_prompt_path}"
        excel_actor.gen_sys_prompt(read_system_prompt_md(system_prompt_path))
        excel_actor.write_sys_prompt()
        #
        agentpy_template_path = Path(GAME_NAME) / excel_actor.agentpy_template_path
        assert agentpy_template_path.exists(), f"File not found: {agentpy_template_path}"
        excel_actor.gen_agentpy(read_agentpy_template(agentpy_template_path))
        excel_actor.write_agentpy()
        #
        output[excel_actor.name] = excel_actor
############################################################################################################
def gen_all_stages(sheet: DataFrame, output: Dict[str, ExcelDataStage]) -> None:
    ## 读取Excel文件
    for index, row in sheet.iterrows():
        if pd.isna(row["name"]):
            continue

        excel_stage = ExcelDataStage(row)
        #
        system_prompt_path = Path(GAME_NAME) / excel_stage.sys_prompt_template_path
        assert system_prompt_path.exists(), f"File not found: {system_prompt_path}"
        excel_stage.gen_sys_prompt(read_system_prompt_md(system_prompt_path))
        excel_stage.write_sys_prompt()
        #
        agentpy_template_path = Path(GAME_NAME) / excel_stage.agentpy_template_path
        assert agentpy_template_path.exists(), f"File not found: {agentpy_template_path}"
        excel_stage.gen_agentpy(read_agentpy_template(agentpy_template_path))
        excel_stage.write_agentpy()    
        #
        output[excel_stage.name] = excel_stage 
############################################################################################################
def gen_all_world_system(sheet: DataFrame, output: Dict[str, ExcelDataWorldSystem]) -> None:
    ## 读取Excel文件
    for index, row in sheet.iterrows():
        if pd.isna(row["name"]):
            continue

        excel_world_system = ExcelDataWorldSystem(row)
        #
        system_prompt_path = Path(GAME_NAME) / excel_world_system.sys_prompt_template_path
        assert system_prompt_path.exists(), f"File not found: {system_prompt_path}"
        excel_world_system.gen_sys_prompt(read_system_prompt_md(system_prompt_path))
        excel_world_system.write_sys_prompt()
        #
        agentpy_template_path = Path(GAME_NAME) / excel_world_system.agentpy_template_path
        assert agentpy_template_path.exists(), f"File not found: {agentpy_template_path}"
        excel_world_system.gen_agentpy(read_agentpy_template(agentpy_template_path))
        excel_world_system.write_agentpy()    
        #
        output[excel_world_system.name] = excel_world_system
############################################################################################################
def gen_all_props(sheet: DataFrame, output: Dict[str, ExcelDataProp]) -> None:
    ## 读取Excel文件
    for index, row in sheet.iterrows():
        if pd.isna(row["name"]):
            continue
        excelprop = ExcelDataProp(row)
        output[excelprop.name] = excelprop
############################################################################################################
def analyze_actor_relationship(analyze_data: Dict[str, ExcelDataActor]) -> None:
    #先构建
    for _me in analyze_data.values():
        _me._actor_archives.clear()
        for _other in analyze_data.values():
            _me.add_actor_archive(_other.name)

    #再检查
    for _me in analyze_data.values():
        for _other in analyze_data.values():
            if _me.check_actor_archive(_other.name) and not _other.check_actor_archive(_me.name):
                logger.warning(f"{_me.name} mentioned {_other.name}, but {_other.name} did not mention {_me.name}")
############################################################################################################
def analyze_stage_relationship(analyze_stage_data: Dict[str, ExcelDataStage], analyze_actor_data: Dict[str, ExcelDataActor]) -> None:
    for stage_name, stage_data in analyze_stage_data.items():
        for actor in analyze_actor_data.values():
            actor._stage_archives.clear()
            actor.add_stage_archive(stage_name)
################################################################################################################
def analyze_relationship_between_actors_and_props(analyze_props_data: Dict[str, ExcelDataProp], 
                                                  analyze_actor_data: Dict[str, ExcelDataActor]) -> None:
    #先构建
    for _me in analyze_actor_data.values():
        _me._prop_archives.clear()
        for _others_prop in analyze_props_data.values():
            _me.add_prop_archive(_others_prop.name)
    #再检查
    for _me in analyze_actor_data.values():
        if len(_me._prop_archives) > 0:
            logger.warning(f"{_me.name}: {_me._prop_archives}")
################################################################################################################
def serialization_prop(prop: ExcelDataProp) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    output["name"] = prop.name
    output["codename"] = prop.codename
    output["description"] = prop.description
    output["isunique"] = prop.isunique
    output["type"] = prop.type
    output["attributes"] = [int(attr) for attr in prop.attributes.split(',')]
    output["appearance"] = prop.appearance
    return output       
################################################################################################################
def proxy_prop(prop: ExcelDataProp) -> Dict[str, Any]:
    output: Dict[str, str] = {}
    output['name'] = prop.name
    return output       
################################################################################################################