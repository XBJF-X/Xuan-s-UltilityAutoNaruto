from PySide6.QtWidgets import QDialog

from utils.ui.AddConfig_ui import Ui_AddConfig


class AddConfig(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.UI = Ui_AddConfig()
        self.UI.setupUi(self)

    def get_username(self):
        return self.UI.user_name_LineEdit.text()
