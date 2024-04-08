from auxiliary.chaos_engineering_system import IChaosEngineering
from loguru import logger
from auxiliary.builders import WorldDataBuilder
from typing import Any

## 运行中的测试系统, 空的混沌工程系统
class ChaosBuddingWorld(IChaosEngineering):
    
    ##
    def __init__(self, name: str) -> None:
        self.name: str = name

    ##
    def on_pre_create_world(self, extended_context: Any, worlddata: WorldDataBuilder) -> None:
        logger.error(f" {self.name}: on_pre_create_world")

    ##
    def on_post_create_world(self, extended_context: Any, worlddata: WorldDataBuilder) -> None:
        logger.error(f" {self.name}: on_post_create_world")
    
    ##
    def on_read_memory_failed(self, extended_context: Any, name: str, readarchprompt: str) -> None:
        logger.error(f"{self.name}: on_read_memory_failed {name} = {readarchprompt}")