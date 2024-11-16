from enum import StrEnum, unique


@unique
class ComplexStageNameSymbol(StrEnum):
    GUID_FLAG = "%"
    UNKNOWN_STAGE_NAME_TAG = f"未知场景{GUID_FLAG}"


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


class ComplexStageName:

    @staticmethod
    def generate_unknown_stage_name(guid: int) -> str:
        return f"{ComplexStageNameSymbol.UNKNOWN_STAGE_NAME_TAG}{guid}"

    ################################################################################################################################################
    def __init__(self, source_name: str) -> None:
        self._source_name: str = source_name

    ################################################################################################################################################
    @property
    def source_name(self) -> str:
        return str(self._source_name)

    ################################################################################################################################################
    @property
    def is_unknown_stage_name(self) -> bool:
        return ComplexStageNameSymbol.UNKNOWN_STAGE_NAME_TAG in self.source_name

    ################################################################################################################################################
    @property
    def extract_guid(self) -> int:
        if not self.is_unknown_stage_name:
            return 0
        return int(self.source_name.split(ComplexStageNameSymbol.GUID_FLAG)[1])

    ################################################################################################################################################
