"""场景图（**唯一实现**在 ``backend/core/scene_graph.py``，本模块仅保留旧 import 路径）

阶段 3 去重：改前两份实现近乎逐字复制，但**行为不同** ——
``core/scene_graph.py`` 在推导 gray/mask 后把 ``element.bgra = None``（内存优化，
实测单进程省 ~14MB），而 ``legacy/Scene/SceneGraph.py`` 用
``np.ascontiguousarray(bgra)`` **保留** 4 通道大数组。运行时共享单例由 core 版本构建
（``services/scheduler_service.get_shared_scene_graph``），识别器却由旧层类型驱动 →
同一进程内 ``element.bgra`` 语义（None / bytes / ndarray）不统一。

现在本模块再导出 core 版本（保留 ``bgra=None`` 优化），``Recognizer`` / ``Operationer`` /
``api/resource.py`` 与 test_scene 里的 6 处 import 全部继续可用且行为一致。
"""
from backend.core.scene_graph import SceneGraph  # noqa: F401

__all__ = ["SceneGraph"]
