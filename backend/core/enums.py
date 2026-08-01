"""枚举定义 - 从 utils/Base/Enums.py 迁移（纯 Python，无依赖）"""
import enum


class ElementType(enum.IntEnum):
    """元素类型"""
    IMG = 0
    COORDINATE = 1


class MatchType(enum.IntEnum):
    """图像匹配类型"""
    TEMPLATE = 0
    SIFT = 1


class KEY_INDEX(enum.IntEnum):
    """按键类型枚举"""
    BasicAttack = 0       # 平A
    FirstSkill = 1        # 一技能
    SecondSkill = 2       # 二技能
    UltimateSkill = 3     # 奥义
    LeftSubSkill = 4      # 左子技能
    RightSubSkill = 5     # 右子技能
    Substitution = 6      # 替身
    SecretScroll = 7      # 秘卷
    Summon = 8            # 通灵
    JoyStick = 9          # 摇杆
