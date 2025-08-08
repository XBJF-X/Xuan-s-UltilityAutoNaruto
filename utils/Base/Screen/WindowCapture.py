import logging

import win32gui
import win32ui
import win32con
import numpy as np
import cv2
import time
import ctypes
from ctypes import windll, WinDLL, wintypes

from utils.Config import Config

# 提前加载user32库并定义PrintWindow函数（减少每次调用的开销）
user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
user32.PrintWindow.restype = wintypes.BOOL

# 定义钩子回调函数类型
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)


class WindowSizeListener:
    def __init__(self, hwnd):
        self.hwnd = hwnd  # 目标窗口句柄
        self.hook_id = None  # 钩子ID
        self.running = False  # 监听状态
        self.old_width = 0
        self.old_height = 0

        # 初始化窗口初始大小
        rect = win32gui.GetWindowRect(self.hwnd)
        self.old_width = rect[2] - rect[0]
        self.old_height = rect[3] - rect[1]

    def hook_callback(self, nCode, wParam, lParam):
        """钩子回调函数，处理消息"""
        if nCode >= 0:
            # 解析消息结构
            msg = ctypes.wintypes.MSG.from_address(lParam)

            # 检测WM_SIZE消息
            if msg.hwnd == self.hwnd and msg.message == win32con.WM_SIZE:
                # 获取新的窗口尺寸
                new_width = ctypes.wintypes.LOWORD(msg.lParam)
                new_height = ctypes.wintypes.HIWORD(msg.lParam)

                # 只在尺寸实际改变时触发
                if new_width != self.old_width or new_height != self.old_height:
                    print(f"窗口大小改变: {self.old_width}x{self.old_height} → {new_width}x{new_height}")
                    self.old_width = new_width
                    self.old_height = new_height

        # 传递消息给下一个钩子
        return ctypes.windll.user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def start_listening(self):
        """开始监听消息"""
        self.running = True

        # 创建钩子回调函数
        self.hook_func = HOOKPROC(self.hook_callback)

        # 设置WH_GETMESSAGE钩子，监听所有消息
        self.hook_id = ctypes.windll.user32.SetWindowsHookExW(
            win32con.WH_GETMESSAGE,  # 消息钩子类型
            self.hook_func,
            None,
            ctypes.windll.kernel32.GetCurrentThreadId()  # 监听当前线程消息
        )

        if not self.hook_id:
            raise ctypes.WinError(ctypes.get_last_error())

        print(f"开始监听窗口(句柄: {self.hwnd})的大小变化...")

        # 启动消息循环
        self.msg_loop()

    def msg_loop(self):
        """消息循环，持续获取并处理消息"""
        msg = ctypes.wintypes.MSG()
        while self.running and ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

    def stop_listening(self):
        """停止监听并清理资源"""
        self.running = False
        if self.hook_id:
            ctypes.windll.user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
        print("已停止监听窗口大小变化")

    def __del__(self):
        self.stop_listening()


class WindowCapture:

    width2height = {
        2560: 1440,
        1920: 1080,
        1600: 900,
        1280: 720
    }

    def __init__(self, config: Config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
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
        except Exception:  # 初始化失败时立即清理
            self.release()
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
                self.logger.warning(f"未找到窗口: 标题={window_title}")
            else:
                self.logger.info(f"找到窗口: 标题={window_title}")
                return hwnd
        for window_class in self.config.get_config("窗口类名"):
            hwnd = win32gui.FindWindow(window_class, None)
            if not hwnd:
                self.logger.warning(f"未找到窗口: 类名={window_class}")
            else:
                self.logger.info(f"找到窗口: 类名={window_class}")
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

# if __name__ == "__main__":
#     l = WindowSizeListener(hwnd=win32gui.FindWindow(None, "雷电模拟器"))
#     l.start_listening()
