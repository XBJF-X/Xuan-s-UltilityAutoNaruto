"""配置模型（**唯一实现**在 ``backend/core/config_model.py``，本模块仅保留旧 import 路径）

阶段 3 去重：改前 ``core/config_model.py``(259 行) 与 ``legacy/Config.py``(268 行) 是
近乎逐字复制的**两个同名 Config 类**（方法集完全相同、前 120 行逐字相同），而运行时
真实类型是 ``core.config_model.Config``（由 ``services/config_service.py`` 创建）；
``legacy/Config.py`` 只被 16 处 import 做类型标注 —— 于是"改一处漏一处"、``isinstance``
与 ``mock.patch("backend.core.legacy.Config...")`` 会失效。

现在本模块再导出同一个类，两条 import 路径指向同一对象。
"""
from backend.core.config_model import Config  # noqa: F401

__all__ = ["Config"]
