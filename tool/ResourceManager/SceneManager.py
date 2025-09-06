import ctypes
import logging
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QApplication, QDialog

from StaticFunctions import get_real_path
from tool.ResourceManager.NewScene import NewScene
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.SceneGraphView import SceneGraphView
from ui.SceneManager_ui import Ui_SceneManager


class SceneManager(QMainWindow):
    def __init__(self, scenes_path=Path(get_real_path("src"))):
        super().__init__()
        self.UI = Ui_SceneManager()
        self.UI.setupUi(self)
        self.logger = logging.getLogger("场景管理器")
        self.resource_manager = ResourceDBManager(scenes_path)
        self.scene_graph_view = SceneGraphView(self.resource_manager, self.UI.centralwidget)
        self.UI.horizontalLayout.addWidget(self.scene_graph_view)
        self.UI.refresh.triggered.connect(self._handle_refresh)
        self.UI.new_node.triggered.connect(self._handle_new_node)
        self.UI.save.triggered.connect(self._handle_save)
        self.UI.auto_layout.triggered.connect(lambda: self.scene_graph_view.auto_layout(2000))

    def _handle_refresh(self):
        self.scene_graph_view.init()

    def _handle_new_node(self):
        # 创建 NewSceneNode 对话框实例，传入资源管理器
        nsn = NewScene(self.resource_manager, self.scene_graph_view)
        # 显示模态对话框（用户必须完成操作才能返回）
        result = nsn.exec()  # 阻塞当前流程，直到对话框关闭

        # 根据对话框返回结果进行后续处理
        if result == QDialog.DialogCode.Accepted:
            self.logger.debug(f"确认创建新场景节点")
        else:
            self.logger.debug("取消创建新场景节点")

    def _handle_save(self):
        pass
        # self.resource_manager.save_global_info()


# 配置日志系统
def setup_logging():
    # 创建基础日志格式
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # 创建基础配置
    logging.basicConfig(
        level=logging.DEBUG,  # 设置默认日志级别
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)  # 输出到控制台
        ]
    )

    # 获取根日志记录器
    logger = logging.getLogger()

    # 设置更详细的日志格式（可选）
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 更新所有处理器的格式
    for handler in logger.handlers:
        handler.setFormatter(formatter)

    # 设置特定模块的日志级别（可选）
    # logging.getLogger("PySide6").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger


if __name__ == "__main__":
    # 设置日志系统
    logger = setup_logging()
    # 1. 首先设置DPI感知 - 使用兼容性更好的旧版API
    if sys.platform == 'win32':
        try:
            # 使用兼容性更好的旧版API
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception as e:
            print(f"设置DPI感知失败: {e}")

    # 2. 创建应用实例前设置高DPI策略
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    # 3. 创建应用实例
    app = QApplication(sys.argv)

    # 4. 设置高DPI缩放策略（可选）
    # 在PySide6 6.4+版本中，这步可能不需要
    # app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    sm = SceneManager()
    sm.show()
    sys.exit(app.exec())
