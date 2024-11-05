from entitas import Matcher, Entity  # type: ignore
from typing import List, Optional, Set
from overrides import override
from loguru import logger
from my_components.components import (
    WorldComponent,
    StageComponent,
    ActorComponent,
    PlayerComponent,
    RPGAttributesComponent,
    AppearanceComponent,
    BodyComponent,
    GUIDComponent,
    RPGCurrentWeaponComponent,
    RPGCurrentClothesComponent,
    StageGraphComponent,
    KickOffContentComponent,
    RoundEventsComponent,
    KickOffFlagComponent,
    StageSpawnerComponent,
)
from rpg_game.rpg_entitas_context import RPGEntitasContext
from rpg_game.rpg_game_resource import RPGGameResource
from extended_systems.files_def import PropFile
from rpg_game.base_game import BaseGame
import extended_systems.file_system_helper
from rpg_game.rpg_entitas_processors import RPGEntitasProcessors
from my_models.models_def import (
    ActorInstanceModel,
    StageInstanceModel,
    ActorModel,
    StageModel,
    WorldSystemModel,
    WorldSystemInstanceModel,
    PropFileModel,
    AgentEvent,
    UpdateAppearanceEvent,
)
from my_models.models_def import AttributesIndex
from player.player_proxy import PlayerProxy
import gameplay_systems.public_builtin_prompt as public_builtin_prompt


class RPGGame(BaseGame):
    """
    RPG 的测试类游戏
    """

    def __init__(self, name: str, context: RPGEntitasContext) -> None:
        # 必须实现父
        super().__init__(name)

        ## 尽量不要再加东西了，Game就只管上下文，创建世界的数据，和Processors。其中上下文可以做运行中的全局数据管理者
        self._entitas_context: RPGEntitasContext = context
        self._entitas_context._game = self

        self._game_resource: Optional[RPGGameResource] = None
        self._processors: RPGEntitasProcessors = RPGEntitasProcessors.create(
            self, context
        )
        self._players: List[PlayerProxy] = []
        self._runtime_game_round: int = 0

    ###############################################################################################################################################
    @property
    def runtime_game_round(self) -> int:
        return self._runtime_game_round

    ###############################################################################################################################################
    @property
    def players(self) -> List[PlayerProxy]:
        return self._players

    ###############################################################################################################################################
    @property
    def about_game(self) -> str:
        if self._game_resource is None:
            return ""
        return self._game_resource.about_game

    ###############################################################################################################################################
    def build(self, game_resource: RPGGameResource) -> "RPGGame":

        context = self._entitas_context

        # 混沌系统，准备测试
        context._chaos_engineering_system.on_pre_create_game(context, game_resource)

        ## 第1步，设置根路径
        self._game_resource = game_resource
        ##
        context._langserve_agent_system.set_runtime_dir(game_resource._runtime_dir)
        context._file_system.set_runtime_dir(game_resource._runtime_dir)

        ## 第2步 创建管理员类型的角色，全局的AI
        self._create_world_system_entities(game_resource)

        ## 第3步，创建actor，player是特殊的actor
        player_entities = self._create_player_entities(
            game_resource, game_resource.player_instances
        )
        actor_entities = self._create_actor_entities(
            game_resource, game_resource.actor_instances
        )

        ## 第4步，创建stage
        self._create_stage_entities(game_resource)

        ## 第5步，最后处理因为需要上一阶段的注册流程
        self._initialize_actor_stage_links(set(player_entities + actor_entities))

        ## 第6步，如果是载入的文件，就需要直接修改一些值
        if game_resource.is_load:
            self._load_game(context, game_resource)

        ## 最后！混沌系统，准备测试
        context._chaos_engineering_system.on_post_create_game(context, game_resource)

        return self

    ###############################################################################################################################################
    @override
    def execute(self) -> None:

        # 顺序不要动
        current_processors = self._processors
        if not current_processors._initialized:
            current_processors._initialized = True
            current_processors.activate_reactive_processors()
            current_processors.initialize()

        current_processors.execute()
        current_processors.cleanup()

    ###############################################################################################################################################
    @override
    async def a_execute(self) -> None:

        # 顺序不要动
        current_processors = self._processors
        if not current_processors._initialized:
            current_processors._initialized = True
            current_processors.activate_reactive_processors()
            current_processors.initialize()

        await current_processors.a_execute()
        current_processors.cleanup()

    ###############################################################################################################################################
    @override
    def exit(self) -> None:

        all = [self._processors]
        for processor in all:
            processor.tear_down()
            processor.clear_reactive_processors()

        logger.info(f"{self._name}, game over!!!!!!!!!!!!!!!!!!!!")

    ###############################################################################################################################################
    def _create_world_system_entities(
        self, game_resource: RPGGameResource
    ) -> List[Entity]:

        assert game_resource is not None
        assert game_resource.data_base is not None

        ret: List[Entity] = []

        for world_system_proxy in game_resource.world_systems_proxy:

            world_system_model = game_resource.data_base.get_world_system(
                world_system_proxy.name
            )
            assert world_system_model is not None

            world_system_entity = self._create_world_system_entity(
                world_system_proxy, world_system_model, self._entitas_context
            )
            assert world_system_entity is not None

            ret.append(world_system_entity)

        return ret

    ###############################################################################################################################################
    def _create_world_system_entity(
        self,
        world_system_instance: WorldSystemInstanceModel,
        world_system_model: WorldSystemModel,
        context: RPGEntitasContext,
    ) -> Entity:

        # 创建实体
        world_system_entity = context.create_entity()
        assert world_system_entity is not None

        # 必要组件
        world_system_entity.add(
            GUIDComponent, world_system_model.name, world_system_instance.guid
        )
        world_system_entity.add(WorldComponent, world_system_model.name)
        world_system_entity.add(KickOffContentComponent, world_system_model.name, "")
        world_system_entity.add(RoundEventsComponent, world_system_model.name, [])

        # 添加扩展子系统的功能: Agent
        context._langserve_agent_system.register_agent(
            world_system_model.name, world_system_model.url
        )

        # 添加扩展子系统的功能: CodeName
        code_name_component_class = (
            context._codename_component_system.register_code_name_component_class(
                world_system_model.name,
                f"""{world_system_model.codename}{world_system_instance.guid}""",
            )
        )
        assert code_name_component_class is not None
        world_system_entity.add(code_name_component_class, world_system_instance.name)

        return world_system_entity

    ###############################################################################################################################################
    def _create_player_entities(
        self, game_resource: RPGGameResource, actors_proxy: List[ActorInstanceModel]
    ) -> List[Entity]:

        assert game_resource is not None

        # 创建player 本质就是创建Actor
        actor_entities = self._create_actor_entities(game_resource, actors_proxy)

        # 为Actor添加PlayerComponent
        for actor_entity in actor_entities:

            assert actor_entity is not None
            assert actor_entity.has(ActorComponent)
            assert not actor_entity.has(PlayerComponent)
            actor_entity.add(PlayerComponent, "")

        return actor_entities

    ###############################################################################################################################################
    def _create_actor_entities(
        self, game_resource: RPGGameResource, actor_instances: List[ActorInstanceModel]
    ) -> List[Entity]:

        assert game_resource is not None
        assert game_resource.data_base is not None

        ret: List[Entity] = []

        for actor_instance in actor_instances:

            actor_model = game_resource.data_base.get_actor(actor_instance.name)
            assert actor_model is not None

            entity = self._create_actor_entity(
                actor_instance, actor_model, self._entitas_context
            )
            assert entity is not None

            ret.append(entity)

        return ret

    ###############################################################################################################################################
    def _create_actor_entity(
        self,
        actor_instance: ActorInstanceModel,
        actor_model: ActorModel,
        context: RPGEntitasContext,
    ) -> Entity:

        if actor_instance.name != actor_model.name:
            assert (
                actor_instance.name == f"""{actor_model.name}#{actor_instance.guid}"""
            ), """注意！你做了批量生成的actor但是生成出现了错误！"""

        # 创建实体
        actor_entity = context.create_entity()

        # 必要组件
        actor_entity.add(GUIDComponent, actor_instance.name, actor_instance.guid)

        actor_entity.add(ActorComponent, actor_instance.name, "")

        actor_entity.add(
            RPGAttributesComponent,
            actor_instance.name,
            actor_model.attributes[AttributesIndex.MAX_HP.value],
            actor_model.attributes[AttributesIndex.CUR_HP.value],
            actor_model.attributes[AttributesIndex.DAMAGE.value],
            actor_model.attributes[AttributesIndex.DEFENSE.value],
        )

        actor_entity.add(
            AppearanceComponent,
            actor_instance.name,
            actor_model.body,
            # hash(actor_model.body),
        )
        actor_entity.add(BodyComponent, actor_instance.name, actor_model.body)

        actor_entity.add(
            KickOffContentComponent, actor_instance.name, actor_model.kick_off_message
        )

        actor_entity.add(RoundEventsComponent, actor_instance.name, [])

        # 添加扩展子系统: Agent
        context._langserve_agent_system.register_agent(
            actor_instance.name, actor_model.url
        )

        # 添加扩展子系统: CodeName
        code_name_component_class = (
            context._codename_component_system.register_code_name_component_class(
                actor_instance.name, f"""{actor_model.codename}{actor_instance.guid}"""
            )
        )
        assert code_name_component_class is not None
        actor_entity.add(code_name_component_class, actor_instance.name)

        # 文件系统：添加道具
        for prop_instance in actor_instance.props:
            ## 重构
            assert self._game_resource is not None
            prop_model = self._game_resource.data_base.get_prop(prop_instance.name)
            if prop_model is None:
                logger.error(f"没有从数据库找到道具：{prop_instance.name}")
                continue

            new_prop_file = PropFile(
                PropFileModel(
                    owner=actor_instance.name,
                    prop_model=prop_model,
                    prop_proxy_model=prop_instance,
                )
            )
            context._file_system.add_file(new_prop_file)
            context._file_system.write_file(new_prop_file)

        # 文件系统：添加档案
        extended_systems.file_system_helper.add_actor_archive_files(
            context._file_system, actor_instance.name, set(actor_model.actor_archives)
        )

        extended_systems.file_system_helper.add_stage_archive_files(
            context._file_system, actor_instance.name, set(actor_model.stage_archives)
        )

        # 文件系统准备好之后，设置当前使用的道具
        weapon_prop_file: Optional[PropFile] = None
        clothes_prop_file: Optional[PropFile] = None
        for prop_name in actor_instance.actor_current_using_prop:

            find_prop_file_weapon_or_clothes = context._file_system.get_file(
                PropFile, actor_instance.name, prop_name
            )
            if find_prop_file_weapon_or_clothes is None:
                logger.error(f"没有找到道具文件：{prop_name}")
                continue

            if find_prop_file_weapon_or_clothes.is_weapon and weapon_prop_file is None:
                weapon_prop_file = find_prop_file_weapon_or_clothes
            elif (
                find_prop_file_weapon_or_clothes.is_clothes
                and clothes_prop_file is None
            ):
                clothes_prop_file = find_prop_file_weapon_or_clothes

        if weapon_prop_file is not None and not actor_entity.has(
            RPGCurrentWeaponComponent
        ):
            actor_entity.add(
                RPGCurrentWeaponComponent, actor_instance.name, weapon_prop_file.name
            )

        if clothes_prop_file is not None and not actor_entity.has(
            RPGCurrentClothesComponent
        ):
            actor_entity.add(
                RPGCurrentClothesComponent, actor_instance.name, clothes_prop_file.name
            )

        return actor_entity

    ###############################################################################################################################################
    def _create_stage_entities(self, game_resource: RPGGameResource) -> List[Entity]:

        assert game_resource is not None

        ret: List[Entity] = []

        for stage_proxy in game_resource.stages_instances:

            stage_model = game_resource.data_base.get_stage(stage_proxy.name)
            assert stage_model is not None

            stage_entity = self._create_stage_entity(
                stage_proxy, stage_model, self._entitas_context
            )
            assert stage_entity is not None

            ret.append(stage_entity)

        return ret

    ###############################################################################################################################################
    def _create_stage_entity(
        self,
        stage_instance: StageInstanceModel,
        stage_model: StageModel,
        context: RPGEntitasContext,
    ) -> Entity:

        assert stage_instance is not None
        assert stage_model is not None
        assert stage_instance.name == stage_model.name
        assert context is not None

        # 创建实体
        stage_entity = context.create_entity()

        # 必要组件
        stage_entity.add(GUIDComponent, stage_model.name, stage_instance.guid)
        stage_entity.add(StageComponent, stage_model.name)

        # 记录属性
        stage_entity.add(
            RPGAttributesComponent,
            stage_model.name,
            stage_model.attributes[AttributesIndex.MAX_HP.value],
            stage_model.attributes[AttributesIndex.CUR_HP.value],
            stage_model.attributes[AttributesIndex.DAMAGE.value],
            stage_model.attributes[AttributesIndex.DEFENSE.value],
        )

        # 记录用
        stage_entity.add(
            KickOffContentComponent, stage_model.name, stage_model.kick_off_message
        )

        # 记录用
        stage_entity.add(RoundEventsComponent, stage_model.name, [])

        # 添加场景可以连接的场景
        stage_entity.add(StageGraphComponent, stage_model.name, stage_model.stage_graph)

        # 添加spawners
        stage_entity.add(
            StageSpawnerComponent, stage_model.name, stage_instance.spawners
        )

        ## 重新设置Actor和stage的关系
        for actor_instance in stage_instance.actors:

            actor_name = actor_instance["name"]
            actor_entity: Optional[Entity] = context.get_actor_entity(actor_name)
            assert actor_entity is not None

            actor_entity.replace(ActorComponent, actor_name, stage_model.name)

        # 场景内添加道具
        for prop_proxy in stage_instance.props:
            # 直接使用文件系统
            assert self._game_resource is not None
            prop_model = self._game_resource.data_base.get_prop(prop_proxy.name)
            if prop_model is None:
                logger.error(f"没有从数据库找到道具：{prop_proxy.name}")
                continue

            prop_file = PropFile(
                PropFileModel(
                    owner=stage_model.name,
                    prop_model=prop_model,
                    prop_proxy_model=prop_proxy,
                )
            )
            context._file_system.add_file(prop_file)
            context._file_system.write_file(prop_file)

        # 添加子系统：Agent
        context._langserve_agent_system.register_agent(
            stage_model.name, stage_model.url
        )

        # 添加子系统：CodeName
        code_name_component_class = (
            context._codename_component_system.register_code_name_component_class(
                stage_model.name, stage_model.codename
            )
        )
        assert code_name_component_class is not None
        stage_entity.add(code_name_component_class, stage_instance.name)

        # 添加子系统：StageTag
        context._codename_component_system.register_stage_tag_component_class(
            stage_model.name, f"""{stage_model.codename}{stage_instance.guid}"""
        )

        return stage_entity

    ###############################################################################################################################################
    def _initialize_actor_stage_links(self, actor_entities: Set[Entity]) -> None:
        # 只有初始化级别的调用，才能使用这个函数
        for actor_entity in actor_entities:
            actor_comp = actor_entity.get(ActorComponent)
            assert actor_comp.current_stage != ""
            self._entitas_context.update_stage_tag_component(
                actor_entity, "", actor_comp.current_stage
            )

    ###############################################################################################################################################
    def add_player(self, player_proxy: PlayerProxy) -> None:
        assert player_proxy not in self._players
        if player_proxy not in self._players:
            self._players.append(player_proxy)

    ###############################################################################################################################################
    def get_player(self, player_name: str) -> Optional[PlayerProxy]:
        for player in self._players:
            if player.name == player_name:
                return player
        return None

    ###############################################################################################################################################
    def _load_game(
        self, context: RPGEntitasContext, game_resource: RPGGameResource
    ) -> None:

        # 存储的局数拿回来
        self._runtime_game_round = game_resource.save_round

        # 重新加载相关的对像
        self._load_entities(context, game_resource)
        self._load_agents(context, game_resource)
        self._load_archives(context, game_resource)
        self._load_players(context, game_resource)  # 必须在最后！

    ###############################################################################################################################################
    def _load_entities(
        self, context: RPGEntitasContext, game_resource: RPGGameResource
    ) -> None:

        assert game_resource.is_load

        load_entities = context.get_group(
            Matcher(
                any_of=[RPGAttributesComponent, AppearanceComponent, PlayerComponent]
            )
        ).entities

        for load_entity in load_entities:

            safe_name = context.safe_get_entity_name(load_entity)
            if safe_name == "":
                continue

            model = game_resource.get_entity_profile(safe_name)
            if model is None:
                continue

            assert model.name == safe_name

            for comp in model.components:

                # 只有这些组件需要处理
                match (comp.name):

                    case RPGAttributesComponent.__name__:
                        rpg_attr_comp = RPGAttributesComponent(**comp.data)
                        load_entity.replace(
                            RPGAttributesComponent,
                            rpg_attr_comp.name,
                            rpg_attr_comp.maxhp,
                            rpg_attr_comp.hp,
                            rpg_attr_comp.attack,
                            rpg_attr_comp.defense,
                        )

                    case AppearanceComponent.__name__:
                        appearance_comp = AppearanceComponent(**comp.data)
                        load_entity.replace(
                            AppearanceComponent,
                            appearance_comp.name,
                            appearance_comp.appearance,
                            # appearance_comp.hash_code,
                        )

                    case PlayerComponent.__name__:
                        player_comp = PlayerComponent(**comp.data)
                        load_entity.replace(PlayerComponent, player_comp.name)

                    case KickOffFlagComponent.__name__:
                        kick_off_flag_comp = KickOffFlagComponent(**comp.data)
                        load_entity.replace(
                            KickOffFlagComponent, kick_off_flag_comp.name
                        )

                    case _:
                        pass

    ###############################################################################################################################################
    def _load_agents(
        self, context: RPGEntitasContext, game_resource: RPGGameResource
    ) -> None:

        assert game_resource.is_load

        load_entities = context.get_group(
            Matcher(any_of=[ActorComponent, StageComponent])
        ).entities

        for load_entity in load_entities:
            safe_name = context.safe_get_entity_name(load_entity)
            if safe_name == "":
                continue

            chat_history = game_resource.get_chat_history(safe_name)
            if chat_history is None:
                continue

            context._langserve_agent_system.fill_chat_history(safe_name, chat_history)

    ###############################################################################################################################################
    def _load_archives(
        self, context: RPGEntitasContext, game_resource: RPGGameResource
    ) -> None:

        assert game_resource.is_load

        load_entities = context.get_group(
            Matcher(any_of=[ActorComponent, StageComponent])
        ).entities

        for load_entity in load_entities:
            safe_name = context.safe_get_entity_name(load_entity)
            if safe_name == "":
                continue

            actor_archives = game_resource.get_actor_archives(safe_name)
            extended_systems.file_system_helper.load_actor_archive_files(
                context._file_system, safe_name, actor_archives
            )

            stage_archives = game_resource.get_stage_archives(safe_name)
            extended_systems.file_system_helper.load_stage_archive_files(
                context._file_system, safe_name, stage_archives
            )

    ###############################################################################################################################################
    def _load_players(
        self, context: RPGEntitasContext, game_resource: RPGGameResource
    ) -> None:

        assert game_resource.is_load
        player_entities = context.get_group(Matcher(any_of=[PlayerComponent])).entities

        for player_entity in player_entities:

            player_comp = player_entity.get(PlayerComponent)
            player_proxy_model = game_resource.get_player_proxy(player_comp.name)
            if player_proxy_model is None:
                continue

            player_proxy = PlayerProxy(player_proxy_model)
            self.add_player(player_proxy)
            player_proxy.on_load()

    ###############################################################################################################################################
    def add_message_to_players(
        self, player_entities: Set[Entity], agent_event: AgentEvent
    ) -> None:

        if self._ignore_agent_event(agent_event):
            logger.debug(f"忽略的消息：{agent_event}")
            return

        for player_entity in player_entities:
            assert player_entity.has(PlayerComponent)
            player_comp = player_entity.get(PlayerComponent)
            player_proxy = self.get_player(player_comp.name)
            if player_proxy is None:
                assert False, f"没有找到玩家：{player_comp.name}"
                continue

            assert player_proxy.actor_name != ""
            agent_event.message_content = public_builtin_prompt.replace_you(
                agent_event.message_content,
                player_proxy.actor_name,
            )

            player_proxy.add_actor_message(player_proxy.actor_name, agent_event)

    ###############################################################################################################################################
    def _ignore_agent_event(self, agent_event: AgentEvent) -> bool:
        return isinstance(agent_event, UpdateAppearanceEvent)

    ###############################################################################################################################################
    def runtime_create_actor_entity(
        self,
        actor_instance: ActorInstanceModel,
        actor_model: ActorModel,
        stage_entity: Entity,
    ) -> Optional[Entity]:

        logger.warning(
            f"runtime_create_actor_entity: {actor_instance.name}, !!!!!!!!!!!!!!!!!!!!!"
        )

        assert stage_entity.has(StageComponent)
        actor_entity = self._create_actor_entity(
            actor_instance, actor_model, self._entitas_context
        )
        if actor_entity is None:
            return None

        actor_comp = actor_entity.get(ActorComponent)
        assert actor_comp.current_stage == ""

        # 重新设置值
        stage_comp = stage_entity.get(StageComponent)
        actor_entity.replace(ActorComponent, actor_comp.name, stage_comp.name)

        # 必须使用这个更新
        self._initialize_actor_stage_links(set({actor_entity}))

        return actor_entity

    ###############################################################################################################################################
