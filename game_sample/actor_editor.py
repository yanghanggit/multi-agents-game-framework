import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
from typing import List, Dict, Any, Optional, cast
from game_sample.prop_data import ExcelDataProp
from game_sample.actor_data import ExcelDataActor
from game_sample.guid_generator import editor_guid_generator
from rpg_models.entity_models import (
    ActorModel,
    Attributes,
    ActorInstanceModel,
    PropInstanceModel,
)
from rpg_models.editor_models import EditorEntityType, EditorProperty
import format_string.ints_string
import format_string.complex_prop_name
from format_string.complex_actor_name import ComplexActorName


class ExcelEditorActor:

    def __init__(
        self,
        data: Any,
        actor_data_base: Dict[str, ExcelDataActor],
        prop_data_base: Dict[str, ExcelDataProp],
        group_generation_id: int = 0,
    ) -> None:

        #
        assert data is not None
        assert actor_data_base is not None
        assert prop_data_base is not None

        #
        self._data: Any = data
        self._actor_data_base: Dict[str, ExcelDataActor] = actor_data_base
        self._prop_data_base: Dict[str, ExcelDataProp] = prop_data_base
        self._guid = group_generation_id
        self._complex_name: ComplexActorName = ComplexActorName(
            str(data[EditorProperty.NAME])
        )

        # 检查actor类型是否合法
        if self.type not in [
            EditorEntityType.PLAYER,
            EditorEntityType.ACTOR,
            EditorEntityType.GROUP,
        ]:
            assert False, f"Invalid actor type: {self.type}"

    #################################################################################################################################

    @property
    def name(self) -> str:
        return self._complex_name.source_name

    #################################################################################################################################
    @property
    def data_base_name(self) -> str:
        return self._complex_name.actor_name

    #################################################################################################################################
    @property
    def format_actor_name_with_guid(self) -> str:
        return ComplexActorName.format_name_with_guid(
            self.data_base_name, self._resolve_guid()
        )

    #################################################################################################################################
    @property
    def agent_name(self) -> str:
        if self._complex_name.is_complex_name:
            return self.format_actor_name_with_guid

        assert self.name == self.data_base_name
        return self.name

    #################################################################################################################################
    @property
    def excel_data(self) -> Optional[ExcelDataActor]:
        assert self._data is not None
        return self._actor_data_base[self.data_base_name]

    #################################################################################################################################
    @property
    def type(self) -> str:
        return cast(str, self._data[EditorProperty.TYPE])

    #################################################################################################################################
    @property
    def attributes(self) -> List[int]:
        assert self._data is not None
        data = cast(str, self._data[EditorProperty.ATTRIBUTES])
        assert "," in data, f"raw_string_val: {data} is not valid."
        values = format_string.ints_string.convert_string_to_ints(data)
        if len(values) < Attributes.MAX:
            values.extend([0] * (Attributes.MAX - len(values)))
        return values

    #################################################################################################################################
    @property
    def kick_off_message(self) -> str:
        assert self._data is not None
        if self._data[EditorProperty.KICK_OFF_MESSAGE] is None:
            return "无"
        return cast(str, self._data[EditorProperty.KICK_OFF_MESSAGE])

    #################################################################################################################################
    @property
    def system_prompt(self) -> str:
        assert self.excel_data is not None
        return self.excel_data._gen_system_prompt

    #################################################################################################################################
    @property
    def actor_equipped_props(self) -> List[str]:
        assert self._data is not None
        raw_string = cast(str, self._data[EditorProperty.ACTOR_EQUIPPED_PROPS])
        if raw_string is None:
            return []
        return [str(attr) for attr in raw_string.split(";")]

    #################################################################################################################################
    @property
    def actor_props(self) -> List[str]:
        data: Optional[str] = self._data[EditorProperty.ACTOR_PROPS]
        if data is None:
            return []

        split_data = data.split(";")
        return [prop for prop in split_data if prop != ""]

    #################################################################################################################################
    @property
    def codename(self) -> str:
        assert self.excel_data is not None
        return self.excel_data.codename

    #################################################################################################################################
    def parse_actor_prop(self) -> List[tuple[ExcelDataProp, int]]:

        ret: List[tuple[ExcelDataProp, int]] = []

        for prop_info in self.actor_props:
            if prop_info == "":
                continue

            parse = format_string.complex_prop_name.parse_complex_prop_name(prop_info)
            prop_name = parse[0]
            prop_count = parse[1]

            if prop_name not in self._prop_data_base:
                assert False, f"Invalid prop: {prop_name}"
                continue

            ret.append((self._prop_data_base[prop_name], prop_count))

        return ret

    #################################################################################################################################

    def gen_model(self) -> ActorModel:

        assert self.excel_data is not None

        return ActorModel(
            name=self.data_base_name,
            codename=self.codename,
            url=self.excel_data.localhost_api_url,
            system_prompt=self.system_prompt,
            kick_off_message=self.kick_off_message,
            actor_archives=self.excel_data._actor_archives,
            stage_archives=self.excel_data._stage_archives,
            attributes=self.attributes,
            base_form=self.excel_data.base_form,
        )

    #################################################################################################################################
    def gen_instance(self) -> ActorInstanceModel:
        assert self.excel_data is not None
        ret: ActorInstanceModel = ActorInstanceModel(
            name="",
            guid=self._resolve_guid(),
            props=[],
            actor_equipped_props=self.actor_equipped_props,
        )

        if self._complex_name.is_complex_name:
            ret.name = self.format_actor_name_with_guid
        else:
            ret.name = self.name

        for tp in self.parse_actor_prop():
            ret.props.append(
                PropInstanceModel(
                    name=tp[0].name,
                    guid=editor_guid_generator.gen_prop_guid(tp[0].name),
                    count=tp[1],
                )
            )

        # test
        if ComplexActorName.contains_guid(ret.name):
            assert (
                ret.name == self.format_actor_name_with_guid
            ), f"Invalid actor name: {ret.name}"
        else:
            assert ret.name in self._actor_data_base, f"Invalid actor name: {ret.name}"

        return ret

    #################################################################################################################################
    def _resolve_guid(self) -> int:
        if self._guid > 0:
            return self._guid

        self._guid = editor_guid_generator.gen_actor_guid(self.data_base_name)
        return self._guid

    #################################################################################################################################
