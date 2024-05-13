import os
from typing import List, Optional
from auxiliary.base_data import NPCData, PropData, StageData
from entitas import Processors, Matcher #type: ignore
from loguru import logger
from auxiliary.components import (
    InteractivePropActionComponent,
    WorldComponent,
    StageComponent, 
    ExitOfPrisonComponent,
    NPCComponent, 
    PlayerComponent, 
    SimpleRPGRoleComponent, 
    StageEntryConditionComponent,
    StageExitConditionComponent,
    RoleAppearanceComponent)
from auxiliary.extended_context import ExtendedContext
from auxiliary.builders import WorldDataBuilder, StageBuilder, NPCBuilder
from entitas.entity import Entity
from systems.init_memory_system import InitMemorySystem
from systems.npc_ready_for_planning_system import NPCReadyForPlanningSystem
from systems.stage_planning_system import StagePlanningSystem
from systems.npc_planning_system import NPCPlanningSystem
from systems.speak_action_system import SpeakActionSystem
from systems.attack_action_system import AttackActionSystem
from systems.leave_for_action_system import LeaveForActionSystem
from systems.pre_leave_for_system import PreLeaveForSystem
from systems.director_system import DirectorSystem
from systems.dead_action_system import DeadActionSystem
from systems.destroy_system import DestroySystem
from systems.stage_ready_for_planning_system import StageReadyForPlanningSystem
from systems.tag_action_system import TagActionSystem
from systems.data_save_system import DataSaveSystem
from systems.broadcast_action_system import BroadcastActionSystem  
from systems.interactive_prop_action_system import InteractivePropActionSystem
from systems.whisper_action_system import WhisperActionSystem 
from systems.search_action_system import SearchActionSystem
from systems.mind_voice_action_system import MindVoiceActionSystem
from auxiliary.director_component import StageDirectorComponent
from auxiliary.file_def import PropFile
from systems.begin_system import BeginSystem
from systems.end_system import EndSystem
import shutil
from systems.pre_planning_system import PrePlanningSystem
from systems.post_planning_system import PostPlanningSystem
from systems.pre_action_system import PreActionSystem
from systems.post_action_system import PostActionSystem
from systems.post_fight_system import PostFightSystem
from systems.update_archive_system import UpdateArchiveSystem
from systems.prison_break_action_system import PrisonBreakActionSystem
from systems.perception_action_system import PerceptionActionSystem
from systems.steal_action_system import StealActionSystem
from systems.trade_action_system import TradeActionSystem
from systems.check_status_action_system import CheckStatusActionSystem
from base_game import BaseGame
#from systems.post_conversational_action_system import PostConversationalActionSystem
from systems.init_agents_system import InitAgentsSystem
from auxiliary.file_system_helper import add_npc_archive_files
from systems.my_processors import MyProcessors
from systems.simple_rpg_role_pre_fight_system import SimpleRPGRolePreFightSystem
from systems.test_player_update_client_message_system import TestPlayerUpdateClientMessageSystem
from systems.test_player_post_display_client_message_system import TestPlayerPostDisplayClientMessageSystem

## 控制流程和数据创建
class RPGGame(BaseGame):

    def __init__(self, name: str, context: ExtendedContext) -> None:
        super().__init__(name)
        # 不要再加东西了，Game就只管上下文，创建世界的数据，和Processors。其中上下文可以做运行中的全局数据管理者
        self.extendedcontext: ExtendedContext = context
        self.worlddata: Optional[WorldDataBuilder] = None
        self.processors: MyProcessors = self.createprocessors(self.extendedcontext)
###############################################################################################################################################
    def createprocessors(self, context: ExtendedContext) -> MyProcessors:

        processors = MyProcessors()
       
        ##调试用的系统。监视进入运行之前的状态
        processors.add(BeginSystem(context))
        
        #初始化系统########################
        processors.add(InitAgentsSystem(context)) ### 连接所有agent
        processors.add(InitMemorySystem(context)) ### 第一次读状态, initmemory
       
        #规划逻辑########################
        processors.add(PrePlanningSystem(context)) ######## 在所有规划之前
        processors.add(StageReadyForPlanningSystem(context))
        processors.add(StagePlanningSystem(context))
        processors.add(NPCReadyForPlanningSystem(context))
        processors.add(NPCPlanningSystem(context))
        processors.add(PostPlanningSystem(context)) ####### 在所有规划之后

        ## 第一次抓可以被player看到的信息
        processors.add(TestPlayerUpdateClientMessageSystem(context)) 

        #用户拿到相关的信息，并开始操作与输入!!!!!!!
        from systems.test_player_input_system import TestPlayerInputSystem ### 不这样就循环引用
        processors.add(TestPlayerInputSystem(context, self)) 

        #行动逻辑########################
        processors.add(PreActionSystem(context)) ######## 在所有行动之前 #########################################

        #获取状态与查找信息类的行为
        processors.add(CheckStatusActionSystem(context))
        processors.add(PerceptionActionSystem(context))

        #交流（与说话类）的行为
        processors.add(TagActionSystem(context))
        processors.add(MindVoiceActionSystem(context))
        processors.add(WhisperActionSystem(context))
        processors.add(BroadcastActionSystem(context))
        processors.add(SpeakActionSystem(context))
        #processors.add(PostConversationalActionSystem(context))

        #战斗类的行为
        processors.add(SimpleRPGRolePreFightSystem(context)) #战斗之前需要更新装备
        processors.add(AttackActionSystem(context)) 
        processors.add(PostFightSystem(context))
        processors.add(DeadActionSystem(context)) 
        
        #交互类的行为，在死亡之后，因为死了就不能执行
        processors.add(SearchActionSystem(context)) 
        processors.add(StealActionSystem(context))
        processors.add(TradeActionSystem(context))
        processors.add(InteractivePropActionSystem(context))

        #场景切换类行为，非常重要而且必须在最后
        processors.add(PrisonBreakActionSystem(context)) 
        processors.add(PreLeaveForSystem(context)) 
        processors.add(LeaveForActionSystem(context))

        processors.add(PostActionSystem(context)) ####### 在所有行动之后 #########################################
        #########################################

        #行动结束后导演
        processors.add(DirectorSystem(context))
        #行动结束后更新关系网，因为依赖Director所以必须在后面
        processors.add(UpdateArchiveSystem(context))
        #
        processors.add(TestPlayerPostDisplayClientMessageSystem(context))
        #########################################

        ###最后删除entity与存储数据
        processors.add(DestroySystem(context))
        processors.add(DataSaveSystem(context))

         ##调试用的系统。监视进入运行之后的状态
        processors.add(EndSystem(context))

        return processors
###############################################################################################################################################
    def createworld(self, worlddata: WorldDataBuilder) -> None:
        if worlddata is None or worlddata.data is None:
            logger.error("没有WorldBuilder数据，请检查World.json配置。")
            return
        
        context = self.extendedcontext
        chaos_engineering_system = context.chaos_engineering_system
        
        ## 实际运行的路径
        runtime_dir_for_world = f"{worlddata.runtimepath}{worlddata.name}/"

        # 第0步，yh 目前用于测试!!!!!!!，直接删worlddata.name的文件夹，保证每次都是新的 删除runtime_dir_for_world的文件夹
        if os.path.exists(runtime_dir_for_world):
            shutil.rmtree(runtime_dir_for_world)

        # 混沌系统，准备测试
        chaos_engineering_system.on_pre_create_world(context, worlddata)

        ## 第一步，设置根路径
        self.worlddata = worlddata
        context.agent_connect_system.set_root_path(runtime_dir_for_world)
        context.memory_system.set_root_path(runtime_dir_for_world)
        context.file_system.set_root_path(runtime_dir_for_world)

        ### 第二步 创建实体
        self.create_world_npc_entities(worlddata.world_npc_builder)
        self.create_player_npc_entities(worlddata.player_npc_builder)
        self.create_npc_entities(worlddata.npc_buidler)
        self.add_code_name_component_to_world_and_npcs_when_build()

        ### 第三步，创建stage
        self.create_stage_entities(worlddata.stage_builder)
        
        ## 第四步，最后处理因为需要上一阶段的注册流程
        self.add_code_name_component_stages_when_build()

        self.create_data_base_system(worlddata)

        ## 混沌系统，准备测试
        chaos_engineering_system.on_post_create_world(context, worlddata)
###############################################################################################################################################
    def execute(self) -> None:
        self.started = True

        #顺序不要动！！！！！！！！！
        if not self.inited:
            self.inited = True
            self.processors.activate_reactive_processors()
            self.processors.initialize()
        
        self.processors.execute()
        self.processors.cleanup()
###############################################################################################################################################
    def exit(self) -> None:
        self.processors.clear_reactive_processors()
        self.processors.tear_down()
        logger.info(f"{self.name}, game over")
###############################################################################################################################################
    def create_world_npc_entities(self, npcbuilder: NPCBuilder) -> List[Entity]:

        context = self.extendedcontext
        agent_connect_system = context.agent_connect_system
        memory_system = context.memory_system
        code_name_component_system = context.code_name_component_system
        file_system = context.file_system

        res: List[Entity] = []
        
        if npcbuilder.datalist is None:
            raise ValueError("没有WorldNPCBuilder数据，请检查World.json配置。")
            return res
        
        for builddata in npcbuilder.npcs:
            #logger.debug(f"创建World Entity = {builddata.name}")
            worldentity = context.create_entity()
            res.append(worldentity)

            #必要组件
            worldentity.add(WorldComponent, builddata.name)

            #故意不加NPC组件！！

            #重构
            agent_connect_system.register_actor_agent(builddata.name, builddata.url)
            memory_system.initmemory(builddata.name, builddata.memory)
            code_name_component_system.register_code_name_component_class(builddata.name, builddata.codename)

            # 初步建立关系网（在编辑文本中提到的NPC名字）
            add_npc_archive_files(file_system, builddata.name, builddata.npc_names_mentioned_during_editing_or_for_agent)
            
        return res
###############################################################################################################################################
    def create_player_npc_entities(self, npcbuilder: NPCBuilder) -> List[Entity]:

        context = self.extendedcontext
        agent_connect_system = context.agent_connect_system
        memory_system = context.memory_system
        file_system = context.file_system
        code_name_component_system = context.code_name_component_system
        res: List[Entity] = []

        if npcbuilder.datalist is None:
            raise ValueError("没有PlayerNPCBuilder数据，请检查World.json配置。")
            return res
        
        for builddata in npcbuilder.npcs:
            #logger.debug(f"创建Player npc：{builddata.name}")
            playernpcentity = context.create_entity()
            res.append(playernpcentity)

            #必要组件
            playernpcentity.add(PlayerComponent, "") ##此时没有被玩家控制
            playernpcentity.add(SimpleRPGRoleComponent, builddata.name, builddata.attributes[0], builddata.attributes[1], builddata.attributes[2], builddata.attributes[3])
            playernpcentity.add(NPCComponent, builddata.name, "")
            playernpcentity.add(RoleAppearanceComponent, builddata.role_appearance)
            
            #重构
            agent_connect_system.register_actor_agent(builddata.name, builddata.url)
            memory_system.initmemory(builddata.name, builddata.memory)
            code_name_component_system.register_code_name_component_class(builddata.name, builddata.codename)
           
            # 添加道具
            for prop in builddata.props:
                ## 重构
                createpropfile = PropFile(prop.name, builddata.name, prop)
                file_system.add_prop_file(createpropfile)
                code_name_component_system.register_code_name_component_class(prop.name, prop.codename)

            # 初步建立关系网（在编辑文本中提到的NPC名字）
            add_npc_archive_files(file_system, builddata.name, builddata.npc_names_mentioned_during_editing_or_for_agent)

        return res
###############################################################################################################################################
    def create_npc_entities(self, npcbuilder: NPCBuilder) -> List[Entity]:

        context = self.extendedcontext
        agent_connect_system = context.agent_connect_system
        memory_system = context.memory_system
        file_system = context.file_system
        code_name_component_system = context.code_name_component_system
        res: List[Entity] = []

        if npcbuilder.datalist is None:
            raise ValueError("没有NPCBuilder数据，请检查World.json配置。")
            return res
        
        for builddata in npcbuilder.npcs:
            #logger.debug(f"创建npc：{builddata.name}")
            npcentity = context.create_entity()
            res.append(npcentity)

            # 必要组件
            npcentity.add(NPCComponent, builddata.name, "")
            npcentity.add(SimpleRPGRoleComponent, builddata.name, builddata.attributes[0], builddata.attributes[1], builddata.attributes[2], builddata.attributes[3])
            npcentity.add(RoleAppearanceComponent, builddata.role_appearance)

            #重构
            agent_connect_system.register_actor_agent(builddata.name, builddata.url)
            memory_system.initmemory(builddata.name, builddata.memory)
            code_name_component_system.register_code_name_component_class(builddata.name, builddata.codename)
            
            # 添加道具
            for prop in builddata.props:
                ## 重构
                createpropfile = PropFile(prop.name, builddata.name, prop)
                file_system.add_prop_file(createpropfile)
                code_name_component_system.register_code_name_component_class(prop.name, prop.codename)

            # 初步建立关系网（在编辑文本中提到的NPC名字）
            add_npc_archive_files(file_system, builddata.name, builddata.npc_names_mentioned_during_editing_or_for_agent)

        return res
###############################################################################################################################################
    def create_stage_entities(self, stagebuilder: StageBuilder) -> List[Entity]:

        context = self.extendedcontext
        agent_connect_system = context.agent_connect_system
        memory_system = context.memory_system
        file_system = context.file_system
        code_name_component_system = context.code_name_component_system
        res: List[Entity] = []

        if stagebuilder.datalist is None:
            raise ValueError("没有StageBuilder数据，请检查World.json配置。")
            return res
        
        # 创建stage相关配置
        for builddata in stagebuilder.stages:
            #logger.debug(f"创建Stage：{builddata.name}")
            stageentity = context.create_entity()

            #必要组件
            stageentity.add(StageComponent, builddata.name)
            stageentity.add(StageDirectorComponent, builddata.name) ###
            stageentity.add(SimpleRPGRoleComponent, builddata.name, builddata.attributes[0], builddata.attributes[1], builddata.attributes[2], builddata.attributes[3])
    
            ## 重新设置npc和stage的关系
            for npc in builddata.npcs:
                npcname = npc.name
                findnpcagain: Optional[Entity] = context.getnpc(npcname)
                if findnpcagain is None:
                    #logger.error(f"没有找到npc：{npcname}！！！！！！！！！")
                    raise ValueError(f"没有找到npc：{npcname}！！！！！！！！！")
                    continue

                ## 重新设置npc的stage，做覆盖处理
                findnpcagain.replace(NPCComponent, npcname, builddata.name)
                #logger.debug(f"重新设置npc：{npcname}的stage为：{builddata.name}")
                    
            # 场景内添加道具
            for propinstage in builddata.props:
                # 直接使用文件系统
                createpropfile = PropFile(propinstage.name, builddata.name, propinstage)
                file_system.add_prop_file(createpropfile)
                code_name_component_system.register_code_name_component_class(propinstage.name, propinstage.codename)

            ## 创建入口条件
            enter_condition_set = set()
            for enter_condition in builddata.entry_conditions:
                enter_condition_set.add(enter_condition.condition())
            if len(enter_condition_set) > 0:
                stageentity.add(StageEntryConditionComponent, enter_condition_set)
                #logger.debug(f"{builddata.name}的入口条件为：{enter_condition_set}")

            ## 创建出口条件
            exit_condition_set: set[str] = set()
            for exit_condition in builddata.exit_conditions:
                exit_condition_set.add(exit_condition.condition())
            if len(exit_condition_set) > 0:
                stageentity.add(StageExitConditionComponent, set(exit_condition_set))
                #logger.debug(f"{builddata.name}的出口条件为：{exit_condition_set}")

            ## 添加交互道具组件
            if len(builddata.interactiveprops) > 0:
                stageentity.add(InteractivePropActionComponent, builddata.interactiveprops)

            ## 创建连接的场景用于PrisonBreakActionSystem, 目前如果添加就只能添加一个
            assert len(builddata.exit_of_prison) <= 1
            if  len(builddata.exit_of_prison) > 0:
                exit_prison_and_goto_stage =  next(iter(builddata.exit_of_prison))
                stageentity.add(ExitOfPrisonComponent, exit_prison_and_goto_stage.name)

            #重构
            agent_connect_system.register_actor_agent(builddata.name, builddata.url)
            memory_system.initmemory(builddata.name, builddata.memory)
            code_name_component_system.register_code_name_component_class(builddata.name, builddata.codename)
            code_name_component_system.register_stage_tag_component_class(builddata.name, builddata.codename)

        return res
###############################################################################################################################################
    def add_code_name_component_to_world_and_npcs_when_build(self) -> None:
        context = self.extendedcontext
        code_name_component_system = context.code_name_component_system

        #
        worldentities = context.get_group(Matcher(WorldComponent)).entities
        for entity in worldentities:
            worldcomp: WorldComponent = entity.get(WorldComponent)
            codecompclass = code_name_component_system.get_component_class_by_name(worldcomp.name)
            if codecompclass is not None:
                entity.add(codecompclass, worldcomp.name)

        #
        npcsentities = context.get_group(Matcher(NPCComponent)).entities
        for entity in npcsentities:
            npccomp: NPCComponent = entity.get(NPCComponent)
            codecompclass = code_name_component_system.get_component_class_by_name(npccomp.name)
            if codecompclass is not None:
                entity.add(codecompclass, npccomp.name)
###############################################################################################################################################
    def add_code_name_component_stages_when_build(self) -> None:
        context = self.extendedcontext
        code_name_component_system = context.code_name_component_system

        ## 重新设置npc和stage的关系
        npcsentities = context.get_group(Matcher(NPCComponent)).entities
        for entity in npcsentities:
            npccomp: NPCComponent = entity.get(NPCComponent)
            context.change_stage_tag_component(entity, "", npccomp.current_stage)

        ## 重新设置stage和stage的关系
        stagesentities = context.get_group(Matcher(StageComponent)).entities
        for entity in stagesentities:
            stagecomp: StageComponent = entity.get(StageComponent)
            codecompclass = code_name_component_system.get_component_class_by_name(stagecomp.name)
            if codecompclass is not None:
                entity.add(codecompclass, stagecomp.name)
###############################################################################################################################################
    def create_data_base_system(self, worlddata: WorldDataBuilder) -> None:
        context = self.extendedcontext
        data_base_system = context.data_base_system

        database = worlddata.data.get('database', None)
        if database is None:
            logger.error("没有数据库(database)，请检查World.json配置。")
            return
        
        npcs = database.get('npcs', None)
        if npcs is None:
            logger.error("没有NPC数据内容(npcs)，请检查World.json配置。")
            return
        
        for npc in npcs:
            npc_data = npc.get('npc', None)
            assert npc_data is not None

            data_base_system.add_npc(npc_data.get('name'), NPCData(
                npc_data.get('name'), 
                npc_data.get('codename'), 
                npc_data.get('description'), 
                npc_data.get('memory'), 
                npc_data.get('url'), 
                npc_data.get('attributes'), 
                npc_data.get('role_appearance'), 
                npc_data.get('npc_names_mentioned_during_editing_or_for_agent')
            ))

        stages = database.get('stages', None)
        if stages is None:
            logger.error("没有场景数据内容(stages)，请检查World.json配置。")
            return
        
        for stage in stages:
            print(stage)
            stage_data = stage.get('stage', None)
            assert stage_data is not None

            data_base_system.add_stage(stage_data.get('name'), StageData(
                stage_data.get('name'), 
                stage_data.get('codename'), 
                stage_data.get('description'), 
                stage_data.get('url'), 
                stage_data.get('memory'), 
                stage_data.get('entry_conditions'), 
                stage_data.get('exit_conditions'), 
                stage_data.get('npcs'), 
                stage_data.get('props'), 
                stage_data.get('interactiveprops')
            ))

        props = database.get('props', None)
        if props is None:
            logger.error("没有道具数据内容(props)，请检查World.json配置。")
            return

        for prop_data in props:
            data_base_system.add_prop(prop_data.get('name'), PropData(
                prop_data.get('name'), 
                prop_data.get('codename'), 
                prop_data.get('description'), 
                prop_data.get('isunique'), 
                prop_data.get('type'), 
                prop_data.get('attributes')))
            
        logger.info("创建数据库成功。")
            
###############################################################################################################################################