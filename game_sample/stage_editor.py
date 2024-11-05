import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent  # 将项目根目录添加到sys.path
sys.path.append(str(root_dir))
from loguru import logger
from typing import List, Dict, Any, Optional, cast
from game_sample.excel_data_prop import ExcelDataProp
from game_sample.excel_data_actor import ExcelDataActor
from game_sample.excel_data_stage import ExcelDataStage
import game_sample.utils
from game_sample.editor_guid_generator import editor_guid_generator
from my_models.models_def import (
    EditorEntityType,
    EditorProperty,
    AttributesIndex,
    PropInstanceModel,
    StageModel,
    StageInstanceModel,
)
from game_sample.group_editor import ExcelEditorGroup
import game_sample.configuration as configuration


class ExcelEditorStage:

    def __init__(
        self,
        data: Any,
        actor_data_base: Dict[str, ExcelDataActor],
        prop_data_base: Dict[str, ExcelDataProp],
        stage_data_base: Dict[str, ExcelDataStage],
    ) -> None:

        assert data is not None
        assert actor_data_base is not None
        assert prop_data_base is not None
        assert stage_data_base is not None

        #
        self._data: Any = data
        self._actor_data_base: Dict[str, ExcelDataActor] = actor_data_base
        self._prop_data_base: Dict[str, ExcelDataProp] = prop_data_base
        self._stage_data_base: Dict[str, ExcelDataStage] = stage_data_base
        self._editor_groups: List[ExcelEditorGroup] = []

        if self.type not in [EditorEntityType.STAGE]:
            assert False, f"Invalid Stage type: {self.type}"

    #################################################################################################################################
    @property
    def excel_data(self) -> Optional[ExcelDataStage]:
        assert self._data is not None
        assert self._stage_data_base is not None
        return self._stage_data_base[self._data[EditorProperty.NAME]]

    ################################################################################################################################
    @property
    def name(self) -> str:
        assert self.excel_data is not None
        return self.excel_data.name

    #################################################################################################################################
    @property
    def codename(self) -> str:
        assert self.excel_data is not None
        return self.excel_data.codename

    #################################################################################################################################
    @property
    def type(self) -> str:
        assert self._data is not None
        return cast(str, self._data[EditorProperty.TYPE])

    #################################################################################################################################
    @property
    def attributes(self) -> List[int]:
        assert self._data is not None
        data = cast(str, self._data[EditorProperty.ATTRIBUTES])
        assert "," in data, f"raw_string_val: {data} is not valid."
        values = [int(attr) for attr in data.split(",")]
        if len(values) < AttributesIndex.MAX.value:
            values.extend([0] * (AttributesIndex.MAX.value - len(values)))
        return values

    ################################################################################################################################
    @property
    def kick_off_message(self) -> str:
        assert self._data is not None
        return cast(str, self._data[EditorProperty.KICK_OFF_MESSAGE])

    ################################################################################################################################
    @property
    def stage_graph(self) -> List[str]:
        assert self._data is not None
        if self._data[EditorProperty.STAGE_GRAPH] is None:
            return []
        copy_data = str(self._data[EditorProperty.STAGE_GRAPH])
        ret = copy_data.split(";")
        if self.name in ret:
            copy_name = str(self.name)
            ret.remove(copy_name)
        return ret

    ################################################################################################################################
    @property
    def stage_prop(self) -> List[str]:
        data: Optional[str] = self._data[EditorProperty.STAGE_PROP]
        if data is None:
            return []
        return data.split(";")

    ################################################################################################################################
    @property
    def actors_in_stage(self) -> List[str]:
        data: Optional[str] = self._data[EditorProperty.ACTORS_IN_STAGE]
        if data is None:
            return []
        return data.split(";")

    ################################################################################################################################
    def parse_props_in_stage(self) -> List[tuple[ExcelDataProp, int]]:

        ret: List[tuple[ExcelDataProp, int]] = []

        for prop_str in self.stage_prop:
            if prop_str == "":
                continue

            tp = game_sample.utils.parse_prop_info(prop_str)
            if tp[0] not in self._prop_data_base:
                assert False, f"Invalid prop: {tp[0]}"
                continue

            prop_data = self._prop_data_base[tp[0]]
            if not prop_data.can_placed:
                assert False, f"Invalid prop: {prop_data.name}"
                continue

            ret.append((prop_data, tp[1]))

        return ret

    ################################################################################################################################
    def add_stage_graph(self, stage_name: str) -> None:
        stage_graph = self.stage_graph
        if stage_name not in stage_graph:
            stage_graph.append(stage_name)
            self._data[EditorProperty.STAGE_GRAPH] = ";".join(stage_graph)

    ################################################################################################################################
    def parse_actors_in_stage(self) -> List[ExcelDataActor]:

        ret: List[ExcelDataActor] = []

        for actor_name in self.actors_in_stage:
            if actor_name in self._actor_data_base:
                ret.append(self._actor_data_base[actor_name])
            else:
                logger.error(f"Invalid actor: {actor_name}")

        return ret

    ################################################################################################################################
    def gen_prop_instances_in_stage(
        self, props: List[tuple[ExcelDataProp, int]]
    ) -> List[PropInstanceModel]:

        ret: List[PropInstanceModel] = []
        for tp in props:
            new_model = PropInstanceModel(
                name=tp[0].name,
                guid=editor_guid_generator.gen_prop_guid(tp[0].name),
                count=tp[1],
            )
            ret.append(new_model)

        return ret

    ################################################################################################################################
    def gen_actors_instances_in_stage(
        self, actors: List[ExcelDataActor], groups: List[ExcelEditorGroup]
    ) -> List[Dict[str, str]]:
        ret: List[Dict[str, str]] = []

        for actor in actors:
            ret.append({EditorProperty.NAME: actor.name})

        for group in groups:
            for spawn_actor in group.generate_excel_actors:
                ret.append({EditorProperty.NAME: spawn_actor.name})

        return ret

    ################################################################################################################################
    def gen_model(self) -> StageModel:
        assert self.excel_data is not None
        return StageModel(
            name=self.excel_data.name,
            codename=self.excel_data.codename,
            system_prompt=self.excel_data.system_prompt,
            url=self.excel_data.localhost,
            kick_off_message=self.kick_off_message,
            stage_graph=self.stage_graph,
            attributes=self.attributes,
        )

    ################################################################################################################################
    def gen_instance(self) -> StageInstanceModel:
        assert self.excel_data is not None
        #
        ret: StageInstanceModel = StageInstanceModel(
            name=self.excel_data.name,
            guid=editor_guid_generator.gen_stage_guid(self.excel_data.name),
            props=self.gen_prop_instances_in_stage(self.parse_props_in_stage()),
            actors=self.gen_actors_instances_in_stage(
                self.parse_actors_in_stage(), self._editor_groups
            ),
            spawners=self.spawners_in_stage,
        )

        return ret

    ################################################################################################################################
    @property
    def groups_in_stage(self) -> List[str]:
        org_data: Optional[str] = self._data[EditorProperty.GROUPS_IN_STAGE]
        if org_data is None:
            return []
        ret = org_data.split(";")
        return ret

    ################################################################################################################################
    @property
    def spawners_in_stage(self) -> List[str]:

        if not configuration.EN_SPAWNER_FEATURE:
            return []

        org_data: Optional[str] = self._data[EditorProperty.SPAWNERS_IN_STAGE]
        if org_data is None:
            return []
        ret = org_data.split(";")
        return ret

    ################################################################################################################################
    def match_group(self, editor_group: ExcelEditorGroup) -> None:
        for group in self.groups_in_stage:
            if editor_group.equal(group):
                self._editor_groups.append(editor_group)
                break

    ################################################################################################################################
