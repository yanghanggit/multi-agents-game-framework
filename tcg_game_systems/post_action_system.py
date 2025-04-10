from loguru import logger
from entitas import ExecuteProcessor, Matcher  # type: ignore
from typing import Final, FrozenSet, NamedTuple, final, override
from game.tcg_game import TCGGame
from models_v_0_0_1 import ACTION_COMPONENTS_REGISTRY, COMPONENTS_REGISTRY


@final
class PostActionSystem(ExecuteProcessor):

    ############################################################################################################
    def __init__(self, game_context: TCGGame) -> None:
        self._game: TCGGame = game_context

    ############################################################################################################
    @override
    def execute(self) -> None:
        actions_set: Final[FrozenSet[type[NamedTuple]]] = frozenset(
            ACTION_COMPONENTS_REGISTRY.values()
        )
        self._clear_actions(actions_set)
        self._test(actions_set)

    ############################################################################################################
    def _clear_actions(self, registered_actions: FrozenSet[type[NamedTuple]]) -> None:
        entities = self._game.get_group(
            Matcher(any_of=registered_actions)
        ).entities.copy()
        for entity in entities:
            for action_class in registered_actions:
                if entity.has(action_class):
                    logger.debug(
                        f"PostActionSystem: 清理动作: {action_class} from entity: {entity._name}"
                    )
                    entity.remove(action_class)

    ############################################################################################################
    def _test(self, registered_actions: FrozenSet[type[NamedTuple]]) -> None:

        # 动作必须被清理掉。
        entities1 = self._game.get_group(Matcher(any_of=registered_actions)).entities
        assert len(entities1) == 0, f"entities with actions: {entities1}"

        # 动作必须在组件注册表中。
        for action_class in ACTION_COMPONENTS_REGISTRY:
            assert (
                action_class in COMPONENTS_REGISTRY
            ), f"{action_class} not in COMPONENTS_REGISTRY"


############################################################################################################
