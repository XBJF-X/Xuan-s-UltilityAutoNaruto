import ctypes
import time
from ctypes import wintypes

import cv2
import numpy as np
import win32gui
import win32ui

from utils.Base.Config import Config

# 提前加载user32库并定义PrintWindow函数（减少每次调用的开销）
user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
user32.PrintWindow.restype = wintypes.BOOL


class WindowCapture:

    width2height = {
        2560: 1440,
        1920: 1080,
        1600: 900,
        1280: 720
    }

    def __init__(self, config: Config,parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config = config
        self.ready=False
        self.hwnd = None
        self.left = None
        self.top = None
        self.right = None
        self.bottom = None
        self.width = None
        self.height = None
        self.img_buffer = None
        self.save_dc = None
        self.mfc_dc = None
        self.hwnd_dc = None
        self.bmp_handle = None

    def init(self):
        self.callback_all_windows()
        self.hwnd = self.find_hwnd()

        if not self.hwnd:
            raise Exception("未找到目标窗口，请检查窗口是否打开，未被最小化")

        try:
            self._init_gdi_objects()
            self.ready = True
        except Exception:  # 初始化失败时立即清理
            self.release()
            self.logger.error("[WindowCapture]实例化失败")
            self.ready = False
            raise

    def _init_gdi_objects(self):
        """初始化并复用GDI对象和缓冲区，避免每次捕获重复创建"""
        # 获取窗口尺寸
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.hwnd)
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        # print(self.left, self.top, self.right, self.bottom, self.width, self.height)
        if self.width <= 0 or self.height <= 0:
            raise Exception("窗口尺寸无效")
        # 获取窗口DC
        self.hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        self.mfc_dc = win32ui.CreateDCFromHandle(self.hwnd_dc)

        # 创建兼容DC和位图
        self.save_dc = self.mfc_dc.CreateCompatibleDC()
        self.save_bitmap = win32ui.CreateBitmap()
        self.save_bitmap.CreateCompatibleBitmap(self.mfc_dc, self.width, self.height)
        self.save_dc.SelectObject(self.save_bitmap)

        # 缓存位图信息和句柄
        self.bmp_info = self.save_bitmap.GetInfo()
        self.bmp_handle = self.save_bitmap.GetHandle()

        # 预分配numpy数组缓冲区（避免每次创建新数组）
        self.img_buffer = np.empty((self.height, self.width, 4), dtype=np.uint8)

    def screencap(self):
        """捕获窗口画面，支持被遮挡或最小化状态"""
        self._init_gdi_objects()
        # 关键：使用PrintWindow强制绘制窗口内容（即使被遮挡）
        # PW_RENDERFULLCONTENT (0x00000002) 确保捕获完整内容（包括客户区外的部分）
        if not user32.PrintWindow(self.hwnd, self.save_dc.GetSafeHdc(), 0x00000002):
            raise Exception("PrintWindow调用失败，可能权限不足")

        # 将位图数据转换为numpy数组
        bmp_info = self.save_bitmap.GetInfo()
        # print(bmp_info)
        # if bmp_info["bmHeight"] * bmp_info['bmWidth'] < 921600:
        #     self.logger.warning(f"截图出错：{bmp_info}")
        bmp_str = self.save_bitmap.GetBitmapBits(True)
        # print(bmp_str)
        # 转换为BGR格式（OpenCV默认）
        self.img_buffer = np.frombuffer(bmp_str, dtype=np.uint8).reshape(
            (bmp_info['bmHeight'], bmp_info['bmWidth'], 4)
        )
        # print(self.img_buffer.shape)
        bgr = cv2.cvtColor(self.img_buffer, cv2.COLOR_BGRA2BGR)
        new_height = int(self.height * 1600 / self.width)
        if self.width < 1600:
            bgr = cv2.resize(bgr, (1600, new_height), interpolation=cv2.INTER_CUBIC)
        elif self.width > 1600:
            bgr = cv2.resize(bgr, (1600, new_height), interpolation=cv2.INTER_AREA)
        img = bgr[new_height - 900:new_height, 0:1600]
        self.release()
        return img

    def find_hwnd(self):
        """
        查找窗口句柄
        :return: hwnd对象
        """
        for window_title in self.config.get_config("窗口标题"):
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                self.logger.warning(f"未找到窗口: 标题：{window_title}")
            else:
                self.logger.info(f"找到窗口: 标题：{window_title}")
                return hwnd
        for window_class in self.config.get_config("窗口类名"):
            hwnd = win32gui.FindWindow(window_class, None)
            if not hwnd:
                self.logger.warning(f"未找到窗口: 类名：{window_class}")
            else:
                self.logger.info(f"找到窗口: 类名：{window_class}")
                return hwnd

        return None

    def release(self):
        """必须显式调用的资源释放方法"""
        if hasattr(self, 'save_dc') and self.save_dc:
            self.save_dc.DeleteDC()
            self.save_dc = None
        if hasattr(self, 'mfc_dc') and self.mfc_dc:
            self.mfc_dc.DeleteDC()
            self.mfc_dc = None
        if hasattr(self, 'hwnd_dc') and self.hwnd_dc:
            win32gui.ReleaseDC(self.hwnd, self.hwnd_dc)
            self.hwnd_dc = None
        if hasattr(self, 'bmp_handle') and self.bmp_handle:
            win32gui.DeleteObject(self.bmp_handle)
            self.bmp_handle = None
        # self.logger.debug("截图实例资源已清除")

    def callback_all_windows(self):
        """遍历所有窗口并打印类名和标题"""
        windows = []

        def callback(hwnd, extra):
            # 过滤不可见窗口（可选）
            if win32gui.IsWindowVisible(hwnd):
                # 获取窗口标题
                window_title = win32gui.GetWindowText(hwnd)
                # 获取窗口类名
                window_class = win32gui.GetClassName(hwnd)
                if window_title or window_class:  # 过滤空标题和空类名的窗口
                    windows.append((hwnd, window_class, window_title))

        # 枚举所有顶级窗口
        win32gui.EnumWindows(callback, None)

        # 打印结果
        self.logger.debug(f"共找到 {len(windows)} 个可见窗口：")
        self.logger.debug("窗口句柄\t类名\t\t标题")
        self.logger.debug("-" * 80)
        for hwnd, class_name, title in windows:
            self.logger.debug(f"{hwnd}\t{class_name.ljust(15)}\t{title}")

    # 保障2：上下文管理器（with语法自动释放）
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    # 保障3：析构函数兜底（非可靠但必要）
    def __del__(self):
        try:  # 防止析构时抛出异常导致崩溃
            if any([self.save_dc, self.mfc_dc, self.hwnd_dc, self.bmp_handle]):
                self.logger.warning("资源未显式释放! 正在自动清理")
                self.release()
        except Exception:  # 确保析构不会崩溃
            self.logger.error("析构出错")


if __name__ == "__main__":
    try:
        # callback_all_windows()
        # 示例：捕获记事本窗口（标题为"无标题 - 记事本"）
        # 替换为你的目标窗口标题（可通过Spy++工具查看）
        capture = WindowCapture(Config())
        capture.init()
        init_time = time.time()
        for i in range(200):
            start_time = time.time()
            frame = capture.screencap()
            print(f"{(time.time() - start_time) * 1000:.1f}ms")

            # if frame is not None:
            #     # 显示帧率
            #     fps = 1 / (time.time() - start_time)
            #     cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #     cv2.imshow("Window Capture (Even Occluded)", frame)
            #
            # # 按q退出
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        print(f"[平均耗时]：{(time.time() - init_time) * 1000/200:.1f}ms")

    except Exception as e:
        print(f"错误: {e}")
    finally:
        cv2.destroyAllWindows()
        capture.release()

