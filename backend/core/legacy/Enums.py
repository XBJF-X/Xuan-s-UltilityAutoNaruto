"""枚举定义（**唯一实现**在 ``backend/core/enums.py``，本模块仅保留旧 import 路径）

阶段 3 去重：改前 ``core/enums.py`` 与 ``legacy/Enums.py`` 各自定义了一套取值逐字相同的
``ElementType`` / ``MatchType`` / ``KEY_INDEX``（新层 3 处引用、旧层 15 处），任何一处
改动都要双改。现在本模块只做再导出，``from backend.core.legacy.Enums import ElementType``
等 15 处调用点无需改动即可继续工作。
"""
from backend.core.enums import ElementType, KEY_INDEX, MatchType  # noqa: F401

__all__ = ["ElementType", "MatchType", "KEY_INDEX"]
