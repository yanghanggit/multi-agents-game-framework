import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
import os
from loguru import logger
import json
from typing import List, Dict, Any, Set
from budding_world.excel_data import ExcelDataActor, ExcelDataStage, ExcelDataProp, ExcelDataWorldSystem
from budding_world.actor_editor import ExcelEditorActor
from budding_world.stage_editor import ExcelEditorStage
from budding_world.utils import serialization_prop
import pandas as pd

EDITOR_WORLD_TYPE = "World"
EDITOR_PLAYER_TYPE = "Player"
EDITOR_ACTOR_TYPE = "Actor"
EDITOR_STAGE_TYPE = "Stage"
EDITOR_CONFIG_TYPE = "Config"

################################################################################################################
class ExcelEditorWorld:
    def __init__(self, 
                 worldname: str, 
                 data: List[Any], 
                 actor_data_base: Dict[str, ExcelDataActor], 
                 prop_data_base: Dict[str, ExcelDataProp], 
                 stage_data_base: Dict[str, ExcelDataStage],
                 world_system_data_base: Dict[str, ExcelDataWorldSystem]) -> None:
        # 根数据
        self._name: str = worldname
        self._data: List[Any] = data
        self._actor_data_base: Dict[str, ExcelDataActor] = actor_data_base
        self._prop_data_base: Dict[str, ExcelDataProp] = prop_data_base
        self._stage_data_base: Dict[str, ExcelDataStage] = stage_data_base
        self._world_system_data_base: Dict[str, ExcelDataWorldSystem] = world_system_data_base

        #笨一点，先留着吧。。。
        self._world_systems: List[Any] = []
        self._players: List[Any] = []
        self._actors: List[Any] = []
        self._stages: List[Any] = []
        self._config: List[Any] = []

        #真正的构建数据
        self._editor_players: List[ExcelEditorActor] = []
        self._editor_actors: List[ExcelEditorActor] = []
        self._editor_stages: List[ExcelEditorStage] = []
        self._editor_props: List[ExcelDataProp] = []
        self._editor_worlds: List[ExcelEditorActor] = []
        
        ##把数据分类
        self.classify(self._world_systems, self._players, self._actors, self._stages, self._config)
        ##根据分类各种处理。。。
        
        self._editor_players = self.create_players(self._players)
        self._editor_actors = self.create_actors(self._actors)
        self._editor_stages = self.create_stages(self._stages)
        self._editor_worlds = self.create_world_systems(self._world_systems)

        #config = self.about_game()

        ##提取全部的道具。
        allprops = self.parse_props_from_actor(self._editor_players) + self.parse_props_from_actor(self._editor_actors) + self.parse_props_from_stage(self._editor_stages)
        globalnames: Set[str] = set()
        self._editor_props.clear()
        for prop in allprops:
            if prop.name not in globalnames:
                self._editor_props.append(prop)
                globalnames.add(prop.name)
        logger.debug(f"World: {self._name} has {len(self._editor_props)} props.")
################################################################################################################
    @property
    def about_game(self) -> str:
        if len(self._config) == 0:
            return ""
        data = self._config[0]
        about_game: str = ""
        if not pd.isna(data['description']):
            about_game = data['description']
        return about_game
################################################################################################################
    def parse_props_from_actor(self, actors: List[ExcelEditorActor]) -> List[ExcelDataProp]:
        res = []
        for _d in actors:
            for prop in _d.excelprops:
                if prop not in res:
                    res.append(prop)
        return res
################################################################################################################
    def parse_props_from_stage(self, stages: List[ExcelEditorStage]) -> List[ExcelDataProp]:
        res = []
        for stage in stages:

            for prop in stage.props_in_stage:
                if prop not in res:
                    res.append(prop)
            
            # for prop in stage.interactive_props:
            #     if prop not in res:
            #         res.append(prop)

        return res
################################################################################################################
    #先将数据分类
    def classify(self, out_worlds: List[Any], out_players: List[Any], out_actors: List[Any], out_stages: List[Any], out_config: List[Any]) -> None:
        #
        out_worlds.clear()
        out_players.clear()
        out_actors.clear()
        out_stages.clear()
        #
        for item in self._data:
            if item["type"] == EDITOR_WORLD_TYPE:
                out_worlds.append(item)
            elif item["type"] == EDITOR_PLAYER_TYPE:
                out_players.append(item)
            elif item["type"] == EDITOR_ACTOR_TYPE:
                out_actors.append(item)
            elif item["type"] == EDITOR_STAGE_TYPE:
                out_stages.append(item)
            elif item["type"] == EDITOR_CONFIG_TYPE:
                out_config.append(item)
            else:
                logger.error(f"Invalid type: {item['type']}")
################################################################################################################
    def create_world_systems(self, worlds: List[Any]) -> List[Any]:
        return []
################################################################################################################
    def create_players(self, players: List[Any]) -> List[ExcelEditorActor]:
        return self.create_actors(players)
################################################################################################################
    def create_actors(self, actors: List[Any]) -> List[ExcelEditorActor]:
        res: List[ExcelEditorActor] = []
        for item in actors:
            if item['name'] not in self._actor_data_base:
                logger.error(f"Invalid  name: {item['name']}")
                continue
            editor_actor = ExcelEditorActor(item, self._actor_data_base, self._prop_data_base)
            res.append(editor_actor)
        return res
################################################################################################################
    def create_stages(self, stages: List[Any]) -> List[ExcelEditorStage]:
        res: List[ExcelEditorStage] = []
        for item in stages:
            if item['name'] not in self._stage_data_base:
                logger.error(f"Invalid Stage name: {item['name']}")
                continue
            editor_stage = ExcelEditorStage(item, self._actor_data_base, self._prop_data_base, self._stage_data_base)
            res.append(editor_stage)
        return res

    #最后生成JSON
    def serialization(self) -> Dict[str, Any]:
        output: Dict[str, Any] = {}
        #output["worlds"] = [editor_actor.proxy() for editor_actor in self._editor_worlds]
        output["players"] = [editor_actor.proxy() for editor_actor in self._editor_players]
        output["actors"] = [editor_actor.proxy() for editor_actor in self._editor_actors]
        output["stages"] = [editor_stage.proxy() for editor_stage in self._editor_stages]
        output["database"] = self.data_base()

        version_sign = input("请输入版本号:")
        if version_sign == "":
            version_sign = "ewan"
            logger.warning(f"使用默认的版本号: {version_sign}")
        
        output["version"] = version_sign
        output["about_game"] = self.about_game
        return output
    
    def data_base(self) -> Dict[str, Any]:
        output: Dict[str, Any] = {}
        actor_data_base = self._editor_players + self._editor_actors
        output["actors"] = [data.serialization() for data in actor_data_base]
        output["stages"] = [data.serialization() for data in self._editor_stages]
        output["props"] = []
        for prop in self._editor_props:
            output["props"].append(serialization_prop(prop)) #要全的道具数据
        return output
    
    def write(self, directory: str) -> bool:
        builddata = self.serialization()    
        logger.warning(builddata)
        builddata_json = json.dumps(builddata, indent=4, ensure_ascii = False)
        try:
            filename = f"{self._name}.json"
            path = os.path.join(directory, filename)
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(builddata_json)
                return True
        except Exception as e:
            logger.error(f"An error occurred: {e}") 
        return False
################################################################################################################