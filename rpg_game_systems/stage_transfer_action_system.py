from entitas import ReactiveProcessor, Matcher, GroupEvent, Entity  # type: ignore
from game.rpg_game_context import RPGGameContext
from components.actions import (
    StageTransferAction,
)
from components.components import (
    StageComponent,
)
from typing import final, override
from game.rpg_game import RPGGame
import format_string.target_message
import rpg_game_systems.file_system_utils
import rpg_game_systems.action_component_utils
from loguru import logger
import format_string.complex_prop_name
from extended_systems.prop_file import PropFile
from rpg_models.file_models import PropFileModel
from rpg_models.entity_models import PropInstanceModel
from rpg_models.event_models import AgentEvent
from rpg_models.editor_models import GUIDType


####################################################################################################################################
####################################################################################################################################
def _generate_stage_transfer_success_prompt(
    source_name: str, target_name: str, prop_name: str
) -> str:
    return f"""# 放生事件: {source_name} 成功将 {prop_name} 转移至 {target_name}。"""


####################################################################################################################################
####################################################################################################################################
def _generate_stage_transfer_prop_is_not_found_prompt(
    source_name: str, prop_name: str
) -> str:
    return f"""# 提示: {source_name} 试图转移 {prop_name}, 但是失败了。
## 原因分析与建议
{prop_name} 不是一个有效的道具。请 {source_name} 检查道具全名是否正确。"""


####################################################################################################################################
####################################################################################################################################


@final
class StageTransferActionSystem(ReactiveProcessor):

    def __init__(self, context: RPGGameContext, rpg_game: RPGGame):
        super().__init__(context)
        self._context: RPGGameContext = context
        self._game: RPGGame = rpg_game
        self._gen_index: int = 0

    ####################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(StageTransferAction): GroupEvent.ADDED}

    ####################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(StageTransferAction) and entity.has(StageComponent)

    ####################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        for entity in entities:
            self._process_stage_transfer_action(entity)

    ####################################################################################################################################
    def _process_stage_transfer_action(self, stage_entity: Entity) -> None:
        """@A/道具A=1""", """@B/道具B=2"""

        stage_transfer_action = stage_entity.get(StageTransferAction)
        target_and_message = format_string.target_message.extract_target_message_pairs(
            stage_transfer_action.values, "@", "/"
        )

        for target_name, complex_prop_info in target_and_message:

            if (
                rpg_game_systems.action_component_utils.validate_conversation(
                    self._context, stage_entity, target_name
                )
                != rpg_game_systems.action_component_utils.ConversationError.VALID
            ):
                # 不能交谈就是不能交换道具
                logger.warning("不能交谈就是不能交换道具")
                continue

            prop_name, transfer_count = (
                format_string.complex_prop_name.parse_complex_prop_name(
                    complex_prop_info
                )
            )

            assert self._game._game_resource is not None
            assert self._game._game_resource.data_base is not None
            prop_prototype = self._game._game_resource.data_base.get_prop(prop_name)
            if prop_prototype is None:
                logger.error(f"prop_prototype: {prop_name} not found")
                self._notify_stage_transfer_prop_is_not_found(stage_entity, prop_name)
                continue

            new_prop_file = PropFile(
                PropFileModel(
                    owner=target_name,
                    prop_model=prop_prototype,
                    prop_instance_model=PropInstanceModel(
                        name=prop_name, guid=self._gen_prop_guid(), count=transfer_count
                    ),
                )
            )
            self._context.file_system.add_file(new_prop_file)
            self._context.file_system.write_file(new_prop_file)

    ######################################################################################################################################################
    def _notify_stage_transfer_prop_is_not_found(
        self, stage_entity: Entity, prop_name: str
    ) -> None:
        self._context.notify_event(
            set({stage_entity}),
            AgentEvent(
                message=_generate_stage_transfer_prop_is_not_found_prompt(
                    source_name=self._context.safe_get_entity_name(stage_entity),
                    prop_name=prop_name,
                )
            ),
        )

    ####################################################################################################################################
    def _notify_stage_transfer_success(
        self,
        stage_entity: Entity,
        target_entity: Entity,
        prop_name: str,
    ) -> None:
        self._context.notify_event(
            set({stage_entity, target_entity}),
            AgentEvent(
                message=_generate_stage_transfer_success_prompt(
                    source_name=self._context.safe_get_entity_name(stage_entity),
                    target_name=self._context.safe_get_entity_name(target_entity),
                    prop_name=prop_name,
                )
            ),
        )

    ######################################################################################################################################################
    def _gen_prop_guid(self) -> int:
        self._gen_index += 1
        return GUIDType.RUNTIME_PROP_TYPE + self._gen_index

    ######################################################################################################################################################
