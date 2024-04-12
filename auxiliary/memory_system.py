from loguru import logger
import os
from typing import Dict, Set, List
import json

## 所有的初始记忆在这里管理, 目前是测试阶段因为就用一个md来存储是有问题的，后续会改进，比如按着时间来存储并加入数据库？
class MemorySystem:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.rootpath: str = ""
        self.memorydict: Dict[str, str] = {}
        self.relationship: Set[str] = set()

    ### 必须设置根部的执行路行
    def set_root_path(self, rootpath: str) -> None:
        if self.rootpath != "":
            raise Exception(f"[{self.name}]已经设置了根路径，不能重复设置。")
        self.rootpath = rootpath
        logger.debug(f"[{self.name}]设置了根路径为{rootpath}")

    ### 测试的方法
    def memorymdfile(self, who: str) -> str:
        return f"{self.rootpath}{who}/memory.md"
    
    ### 测试的方法
    def relationship_json_file(self, who: str) -> str:
        return f"{self.rootpath}{who}/relationship.json"
    
    ### 删除
    def deletememory(self, who: str) -> None:
        mempath = self.memorymdfile(who)
        try:
            if os.path.exists(mempath):
                os.remove(mempath)
                #logger.debug(f"[{who}]的记忆文件已删除。")
           # else:
                #logger.error(f"[{who}]的记忆文件不存在。")
        except Exception as e:
            #logger.error(f"[{who}]的记忆文件删除失败。")
            return

    ## 核心方法
    def readmemory(self, who: str, initmemory: str) -> None:
        
        mempath = self.memorymdfile(who)
        logger.debug(f"[{who}]的记忆路径为 = [{mempath}]")

        try:

            # 没有就先创建一个！
            if not os.path.exists(mempath):
                os.makedirs(os.path.dirname(mempath), exist_ok=True)
                with open(mempath, "w", encoding="utf-8") as f:
                    f.write(initmemory)

            # 傻傻的读！
            with open(mempath, "r", encoding="utf-8") as f:
                readmemory = f.read()
                logger.debug(f"[!!!!!!!{who}]读取了的记忆 \n{readmemory}")
                self.memorydict[who] = readmemory

        except FileNotFoundError as e:
            logger.error(f"[{who}]的记忆文件不存在。")
            return
        except Exception as e:
            logger.error(f"[{who}]的记忆文件读取失败。")
            return
        
    ###
    def getmemory(self, who: str) -> str:
        return self.memorydict.get(who, "")
    
    ##
    def debug_show_all_memory(self) -> None:
        for who, mem in self.memorydict.items():
            logger.debug(f"[{who}]的记忆为：\n{mem}")

    ##强制写入
    def overwritememory(self, who: str, content: str) -> None:
        mempath = self.memorymdfile(who)
        try:
            if not os.path.exists(mempath):
                os.makedirs(os.path.dirname(mempath), exist_ok=True)
                with open(mempath, "w", encoding="utf-8") as f:
                    f.write(content)
                    logger.debug(f"[{who}]写入了记忆。")
        except Exception as e:
            logger.error(f"[{who}]写入记忆失败。")
            return
        

    ## 初始化关系网
    def initrelationship(self, who: str, relationship: Set[str]) -> None:
        if len(relationship) == 0:
            return
        logger.warning(f"[{who}]的关系网为：{relationship}")
        self.relationship = relationship

    ## 更新关系网
    def addrelationship(self, who: str, update_data: Set[str]) -> None:
        if len(update_data) == 0:
            return
        
        self.relationship = self.relationship | update_data
        logger.warning(f"[{who}]输入新的数据：{update_data}")

    # 写入关系网
    def writerelationship(self, who: str) -> None:
        relationshipjson = self.relationship_json_file(who)
        tolist = list(self.relationship)
        content =  json.dumps(tolist, ensure_ascii = False)
        try:
            # 没有就先创建一个！
            if not os.path.exists(relationshipjson):
                os.makedirs(os.path.dirname(relationshipjson), exist_ok=True)
            with open(relationshipjson, "w", encoding="utf-8") as f:
                f.write(content)
        except FileNotFoundError as e:
            logger.error(f"[{who}]的文件不存在。")
            return
        except Exception as e:
            logger.error(f"[{who}]的文件写入失败。")
            return