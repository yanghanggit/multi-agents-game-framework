from typing import Optional, List


#################################################################################################################################
def _extract_target_message(
    content: str, symbol1: str = "@", symbol2: str = ":"
) -> tuple[Optional[str], Optional[str]]:
    # 检查是否包含'@'和'>'符号
    if symbol1 not in content or symbol2 not in content:
        return None, content

    # 检查'@'是否出现在'>'之前
    at_index = content.find(symbol1)
    gt_index = content.find(symbol2)
    if at_index > gt_index:
        return None, content

    # 提取目标和消息
    try:
        target = content[at_index + 1 : gt_index].strip()
        message = content[gt_index + 1 :].strip()

        # 确保目标和消息不为空
        if not target or not message:
            return None, content

        return target, message
    except Exception as e:
        pass  # 如果有任何异常，返回原始内容和异常提示, 以便调试

    return None, content


#################################################################################################################################
def _has_target_message_format(
    content: str, symbol1: str = "@", symbol2: str = ":"
) -> bool:
    if symbol1 not in content or symbol2 not in content:
        return False
    return True


#################################################################################################################################
def generate_target_message_pair(
    target: str, message: str, symbol1: str = "@", symbol2: str = ":"
) -> str:
    return f"{symbol1}{target}{symbol2}{message}"


#################################################################################################################################
def extract_target_message_pairs(
    values: List[str], symbol1: str = "@", symbol2: str = ":"
) -> List[tuple[str, str]]:

    result: List[tuple[str, str]] = []

    for value in values:
        if not _has_target_message_format(value, symbol1, symbol2):
            continue

        target, message = _extract_target_message(value, symbol1, symbol2)
        if target is None or message is None:
            continue

        result.append((target, message))

    return result


#################################################################################################################################
