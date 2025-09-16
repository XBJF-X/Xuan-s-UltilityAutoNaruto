import logging

from PySide6.QtWidgets import QDialog

from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.SceneGraphView import SceneGraphView
from ui.NewScene_ui import Ui_NewScene


class NewScene(QDialog):

    def __init__(self, resource_manager: ResourceDBManager, scene_graph_view: SceneGraphView):
        super().__init__()
        self.UI = Ui_NewScene()
        self.UI.setupUi(self)
        self.logger = logging.getLogger("新建场景节点")
        self.resource_manager = resource_manager
        self.scene_graph_view = scene_graph_view

        self.UI.confirm.clicked.connect(self._handle_confirm)
        self.UI.cancel.clicked.connect(self._handle_cancel)

    def _handle_confirm(self):
        # 确认操作：添加场景后关闭对话框
        if self.UI.scene_id_LineEdit.text():  # 简单校验：确保场景ID不为空
            self.resource_manager.add_scene(
                name=self.UI.scene_id_LineEdit.text()
            )
            self.scene_graph_view.add_node(self.UI.scene_id_LineEdit.text())
            self.accept()  # 关闭对话框，返回QDialog.Accepted
        else:
            self.logger.warning("场景ID不能为空")

    def _handle_cancel(self):
        # 取消操作：直接关闭对话框
        self.reject()  # 关闭对话框，返回QDialog.Rejected
