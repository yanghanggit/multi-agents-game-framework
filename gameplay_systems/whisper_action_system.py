from entitas import Entity, Matcher, ReactiveProcessor, GroupEvent  # type: ignore
from gameplay_systems.action_components import WhisperAction
from rpg_game.rpg_entitas_context import RPGEntitasContext
from typing import final, override
import gameplay_systems.conversation_helper
import my_format_string.target_and_message_format_string
from rpg_game.rpg_game import RPGGame
import gameplay_systems.public_builtin_prompt as public_builtin_prompt
from my_models.models_def import AgentEvent


################################################################################################################################################
def _generate_whisper_prompt(src_name: str, dest_name: str, content: str) -> str:
    return f"# {public_builtin_prompt.ConstantPrompt.WHISPER_ACTION_TAG} {src_name}对{dest_name}私语道:{content}"


####################################################################################################################################
@final
class WhisperActionSystem(ReactiveProcessor):

    def __init__(self, context: RPGEntitasContext, rpg_game: RPGGame) -> None:
        super().__init__(context)
        self._context: RPGEntitasContext = context
        self._game: RPGGame = rpg_game

    ####################################################################################################################################
    @override
    def get_trigger(self) -> dict[Matcher, GroupEvent]:
        return {Matcher(WhisperAction): GroupEvent.ADDED}

    ####################################################################################################################################
    @override
    def filter(self, entity: Entity) -> bool:
        return entity.has(WhisperAction)

    ####################################################################################################################################
    @override
    def react(self, entities: list[Entity]) -> None:
        for entity in entities:
            self.handle(entity)

    ####################################################################################################################################
    def handle(self, entity: Entity) -> None:
        whisper_action = entity.get(WhisperAction)
        safe_name = self._context.safe_get_entity_name(entity)
        target_and_message = (
            my_format_string.target_and_message_format_string.target_and_message_values(
                whisper_action.values
            )
        )

        for tp in target_and_message:
            if (
                gameplay_systems.conversation_helper.validate_conversation(
                    self._context, entity, tp[0]
                )
                != gameplay_systems.conversation_helper.ConversationError.VALID
            ):
                continue

            target_entity = self._context.get_entity_by_name(tp[0])
            assert target_entity is not None

            self._context.notify_event(
                set({entity, target_entity}),
                AgentEvent(
                    message_content=_generate_whisper_prompt(safe_name, tp[0], tp[1])
                ),
            )


####################################################################################################################################
