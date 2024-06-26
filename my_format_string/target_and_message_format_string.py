from typing import Optional


#################################################################################################################################
# 我方定义的规则字符串
def parse_target_and_message(content: str) -> tuple[Optional[str], Optional[str]]:
    # 检查是否包含'@'和'>'符号
    if "@" not in content or ">" not in content:
        return None, content

    # 检查'@'是否出现在'>'之前
    at_index = content.find("@")
    gt_index = content.find(">")
    if at_index > gt_index:
        return None, content

    # 提取目标和消息
    try:
        target = content[at_index + 1:gt_index].strip()
        message = content[gt_index + 1:].strip()

        # 确保目标和消息不为空
        if not target or not message:
            return None, content

        return target, message
    except Exception as e:
        # 如果有任何异常，返回原始内容和异常提示
        return None, content
#################################################################################################################################
# 是否是有效的目标和消息格式
def is_target_and_message(content: str) -> bool:
    if "@" not in content or ">" not in content:
        return False
    return True
#################################################################################################################################
def make_target_and_message(target: str, message: str) -> str:
    return f"@{target}>{message}"
#################################################################################################################################