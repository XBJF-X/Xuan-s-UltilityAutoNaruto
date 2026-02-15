import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, QOperatingSystemVersion


class AutoThemeApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # 设置初始主题
        self.apply_system_theme()

        # 定时检查主题变化（每2秒检查一次）
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_theme_change)
        self.timer.start(2000)  # 2秒

        self.current_dark_mode = self.is_dark_mode()

    def is_dark_mode(self):
        """检测是否深色模式"""
        if QOperatingSystemVersion.current() >= QOperatingSystemVersion.Windows10:
            try:
                from winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER, KEY_READ
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                with OpenKey(HKEY_CURRENT_USER, key_path, 0, KEY_READ) as key:
                    value, _ = QueryValueEx(key, "AppsUseLightTheme")
                    return value == 0
            except:
                pass
        return False

    def apply_system_theme(self):
        """应用系统主题"""
        is_dark = self.is_dark_mode()

        if is_dark:
            self.setStyleSheet("""
                QMainWindow, QDialog, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel, QPushButton, QCheckBox, QRadioButton {
                    color: #ffffff;
                }
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #3c3c3c;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QDialog, QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QLabel, QPushButton, QCheckBox, QRadioButton {
                    color: #000000;
                }
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
            """)

    def check_theme_change(self):
        """检查主题是否变化"""
        new_dark_mode = self.is_dark_mode()
        if new_dark_mode != self.current_dark_mode:
            self.current_dark_mode = new_dark_mode
            self.apply_system_theme()
            print(f"主题已切换: {'深色' if new_dark_mode else '浅色'}")


# 使用方法
if __name__ == "__main__":
    app = AutoThemeApp(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("自动主题切换")
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())