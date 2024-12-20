from typing import List


#################################################################################################################################
def convert_ints_to_string(values: List[int], symbol: str = ",") -> str:
    return symbol.join(map(str, values))


#################################################################################################################################
def convert_string_to_ints(content: str, symbol: str = ",") -> List[int]:
    return list(map(int, content.split(symbol)))


#################################################################################################################################
