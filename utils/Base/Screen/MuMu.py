import ctypes
import logging
import os
from ctypes import wintypes, c_char_p, c_ubyte

import cv2
import numpy as np

from utils.Base.Config import Config


class MuMu:
    """
    MuMu特化截图，调用MuMu内置的库函数实现截图，特点：
    1.速度快（约7-10ms）
    2.不受模拟器窗口大小位置和可视性的限制，最小化或调整窗口大小或窗口边界超出范围依旧生效
    """

    def __init__(self, config: Config, parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config = config
        self.mumu_handle = 0
        self.display_width = 0
        self.display_height = 0
        self.display_buffer = None
        self.current_mumu_path = None
        self.current_inst_index = None
        self.inited = False
        self.package_name = "com.tencent.KiHan"  # 默认包名

        # 函数指针
        self.connect_func = None
        self.disconnect_func = None
        self.get_display_id_func = None
        self.capture_display_func = None
        self.input_text_func = None
        self.input_event_touch_down_func = None
        self.input_event_touch_up_func = None
        self.input_event_key_down_func = None
        self.input_event_key_up_func = None

        # 定义函数类型
        self.NEMU_HANDLE = ctypes.c_void_p

        # 加载 Windows 库
        self.kernel32 = ctypes.windll.kernel32
        self.LoadLibrary = self.kernel32.LoadLibraryW
        self.GetProcAddress = self.kernel32.GetProcAddress
        self.FreeLibrary = self.kernel32.FreeLibrary

        # 设置函数参数和返回类型
        self.LoadLibrary.argtypes = [wintypes.LPCWSTR]
        self.LoadLibrary.restype = wintypes.HMODULE

        self.GetProcAddress.argtypes = [wintypes.HMODULE, ctypes.c_char_p]
        self.GetProcAddress.restype = ctypes.c_void_p

        self.FreeLibrary.argtypes = [wintypes.HMODULE]
        self.FreeLibrary.restype = wintypes.BOOL

    def init(self):
        """初始化 MuMu 模拟器连接"""
        self.current_mumu_path = self.config.get_config('MuMu安装路径')
        self.current_inst_index = self.config.get_config('MuMu实例索引')
        self.package_name = self.config.get_config('MuMu操作应用包名')

        # 尝试加载 DLL
        self.inited = self.load_mumu_library() and self.connect_mumu() and self.init_screencap()
        return self.inited

    def reload(self):
        """重新加载库和连接"""
        self.inited = self.load_mumu_library() and self.connect_mumu() and self.init_screencap()
        self.logger.debug(f"重新加载库和连接模拟器: {self.inited}")
        return self.inited

    def release(self):
        """释放资源并断开连接"""
        self.inited = False
        self.disconnect_mumu()

    def screencap(self):
        """获取屏幕截图"""
        if not self.capture_display_func:
            self.logger.warning("capture_display_func 函数指针为空")
            return None

        display_id = self.get_display_id()

        ret = self.capture_display_func(
            self.mumu_handle,
            display_id,
            len(self.display_buffer),
            ctypes.byref(ctypes.c_int(self.display_width)),
            ctypes.byref(ctypes.c_int(self.display_height)),
            self.display_buffer
        )

        if ret:
            # 尝试重新加载
            if not self.reload():
                self.logger.warning(f"获取屏幕截图失败，Reload失败. ret={ret}, handle={self.mumu_handle}, "
                                    f"display_id={display_id}, buffer_size={len(self.display_buffer)}, "
                                    f"width={self.display_width}, height={self.display_height}")
                return None

            # 重新尝试
            # 如果返回0说明正常截图
            ret = self.capture_display_func(
                self.mumu_handle,
                display_id,
                len(self.display_buffer),
                ctypes.byref(ctypes.c_int(self.display_width)),
                ctypes.byref(ctypes.c_int(self.display_height)),
                self.display_buffer
            )

            if ret:
                self.logger.warning(f"Reload之后截图失败. ret={ret}, handle={self.mumu_handle}, "
                                    f"display_id={display_id}, buffer_size={len(self.display_buffer)}, "
                                    f"width={self.display_width}, height={self.display_height}")
                return None

        # 转换为 OpenCV 图像
        raw = np.frombuffer(self.display_buffer, dtype=np.uint8).reshape(self.display_height, self.display_width, 4)
        bgr = cv2.cvtColor(raw, cv2.COLOR_RGBA2BGR)
        if bgr.shape[:2] < (900, 1600):
            bgr = cv2.resize(bgr, (1600, 900), interpolation=cv2.INTER_CUBIC)
        elif bgr.shape[:2] > (900, 1600):
            bgr = cv2.resize(bgr, (1600, 900), interpolation=cv2.INTER_AREA)
        dst = cv2.flip(bgr, 0)  # 垂直翻转

        return dst

    def load_mumu_library(self):
        """加载 MuMu 模拟器的 DLL 库"""
        # 尝试不同的 DLL 路径
        new_lib_path = os.path.join(self.current_mumu_path, "nx_device/12.0/shell/sdk/external_renderer_ipc.dll")
        lib_path = os.path.join(self.current_mumu_path, "shell/sdk/external_renderer_ipc.dll")

        dll_handle = None
        if os.path.exists(new_lib_path):
            dll_handle = self.LoadLibrary(new_lib_path)
        if not dll_handle and os.path.exists(lib_path):
            dll_handle = self.LoadLibrary(lib_path)

        if not dll_handle:
            self.logger.warning(f"加载库失败: {new_lib_path} or {lib_path}")
            return False

        # 获取函数地址
        def get_function(func_name, argtypes, restype):
            func_ptr = self.GetProcAddress(dll_handle, func_name.encode('ascii'))
            if not func_ptr:
                return None

            func = ctypes.CFUNCTYPE(restype, *argtypes)(func_ptr)
            return func

        # 定义函数参数和返回类型
        self.connect_func = get_function(
            "nemu_connect",
            [wintypes.LPCWSTR, ctypes.c_int],
            self.NEMU_HANDLE
        )

        self.disconnect_func = get_function(
            "nemu_disconnect",
            [self.NEMU_HANDLE],
            ctypes.c_void_p
        )

        self.get_display_id_func = get_function(
            "nemu_get_display_id",
            [self.NEMU_HANDLE, ctypes.c_char_p, ctypes.c_int],
            ctypes.c_int
        )

        self.capture_display_func = get_function(
            "nemu_capture_display",
            [self.NEMU_HANDLE, ctypes.c_int, ctypes.c_int,
                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_ubyte)],
            ctypes.c_int
        )

        self.input_text_func = get_function(
            "nemu_input_text",
            [self.NEMU_HANDLE, ctypes.c_char_p],
            ctypes.c_int
        )

        # 触摸事件函数
        self.input_event_touch_down_func = get_function(
            "nemu_input_event_touch_down",
            [self.NEMU_HANDLE, ctypes.c_int, ctypes.c_int, ctypes.c_int],
            ctypes.c_int
        )

        self.input_event_touch_up_func = get_function(
            "nemu_input_event_touch_up",
            [self.NEMU_HANDLE, ctypes.c_int, ctypes.c_int, ctypes.c_int],
            ctypes.c_int
        )

        # 按键事件函数
        self.input_event_key_down_func = get_function(
            "nemu_input_event_key_down",
            [self.NEMU_HANDLE, ctypes.c_int],
            ctypes.c_int
        )

        self.input_event_key_up_func = get_function(
            "nemu_input_event_key_up",
            [self.NEMU_HANDLE, ctypes.c_int],
            ctypes.c_int
        )

        # 检查必要的函数是否加载成功
        if not self.connect_func:
            self.logger.warning(f"函数指针获取失败: nemu_connect")
            return False

        if not self.disconnect_func:
            self.logger.warning(f"函数指针获取失败: nemu_disconnect")
            return False

        if not self.capture_display_func:
            self.logger.warning(f"函数指针获取失败: nemu_capture_display")
            return False

        # get_display_id 函数在旧版本中可能不存在，这里只是警告
        if not self.get_display_id_func:
            self.logger.warning("加载 nemu_get_display_id 函数指针失败，请更新模拟器版本")

        return True

    def connect_mumu(self):
        """连接到 MuMu 模拟器实例"""
        if not self.connect_func:
            self.logger.warning("connect_func 函数指针为空")
            return False

        # 连接到模拟器
        self.mumu_handle = self.connect_func(self.current_mumu_path, self.current_inst_index)

        if not self.mumu_handle:
            self.logger.error(f"连接到MuMu模拟器失败: 安装路径={self.current_mumu_path}, 实例化序号={self.current_inst_index}")
            return False
        self.logger.info(f"连接到MuMu模拟器成功: 安装路径={self.current_mumu_path}, 实例化序号={self.current_inst_index}")
        return True

    def init_screencap(self):
        """初始化屏幕捕获功能"""
        if not self.capture_display_func:
            self.logger.warning("capture_display_func 函数指针为空")
            return False

        display_id = self.get_display_id()
        self.logger.debug(f"获取 Display id: {display_id}")

        # 先获取屏幕尺寸
        width = ctypes.c_int()
        height = ctypes.c_int()
        ret = self.capture_display_func(self.mumu_handle, display_id, 0, ctypes.byref(width), ctypes.byref(height), None)

        # 根据文档，这里返回 0 表示成功
        if ret:
            self.logger.warning(f"捕获显示画面失败: ret={ret}, handle={self.mumu_handle}, display_id={display_id}")
            return False

        self.display_width = width.value
        self.display_height = height.value

        # 分配缓冲区 (RGBA 格式)
        buffer_size = self.display_width * self.display_height * 4
        self.display_buffer = (c_ubyte * buffer_size)()

        self.logger.debug(f"Display 初始化: width={self.display_width}, height={self.display_height}, buffer_size={buffer_size}")
        return True

    def get_display_id(self):
        if not self.get_display_id_func:
            self.logger.warning("get_display_id_func_ 函数指针为空，MuMu模拟器版本过低，请升级")
            return 0
        display_id = self.get_display_id_func(self.mumu_handle, c_char_p(self.package_name.encode('utf-8')), 0)
        # self.logger.debug(f"获取Display id : {display_id}")
        if display_id < 0:
            self.logger.warning(f"获取Display id失败：{display_id}")
            return 0
        return display_id

    def disconnect_mumu(self):
        """断开与模拟器的连接"""
        self.logger.debug(f"断开MuMu模拟器连接: Handle={self.mumu_handle}")

        if self.mumu_handle:
            self.disconnect_func(self.mumu_handle)
            self.mumu_handle = 0


if __name__ == "__main__":
    # 创建实例并初始化
    mumu = MuMu(Config())
    if mumu.init():
        print("MuMu emulator initialized successfully!")
        # 捕获屏幕
        # start = time.perf_counter()
        # for i in range(200):
        #     screenshot = mumu.screencap()
        # print(f"{(time.perf_counter() - start) * 1000 / 200:.2f}")
        screenshot = mumu.screencap()
        if screenshot is not None:
            print(f"Captured screenshot: {screenshot.shape}")
            cv2.imshow("MuMu Screenshot", screenshot)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Failed to capture screenshot")

        # 释放资源
        mumu.release()
    else:
        print("Failed to initialize MuMu emulator")
