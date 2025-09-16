import ctypes
import os
from ctypes import wintypes, POINTER, c_void_p, c_uint, c_char, c_ubyte, \
    create_string_buffer
from typing import List, Optional

import cv2
import numpy as np

from utils.Base.Config import Config

# 定义 Windows API 函数
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
CreatePipe = kernel32.CreatePipe
CreateProcessA = kernel32.CreateProcessA
ReadFile = kernel32.ReadFile
CloseHandle = kernel32.CloseHandle
WaitForSingleObject = kernel32.WaitForSingleObject


# 定义结构体和常量
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL)
    ]


class STARTUPINFOA(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPSTR),
        ("lpDesktop", wintypes.LPSTR),
        ("lpTitle", wintypes.LPSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", POINTER(c_char)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE)
    ]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD)
    ]


class LDLIST2(ctypes.Structure):
    """对应 C++ 中的 LDLIST2 结构体，存储模拟器信息"""
    _fields_ = [
        ("index", c_uint),
        ("name", c_char * 64),
        ("topWnd", wintypes.HWND),
        ("bndWnd", wintypes.HWND),
        ("sysboot", wintypes.BOOL),
        ("playerpid", wintypes.DWORD),
        ("vboxpid", wintypes.DWORD),
        ("width", c_uint),
        ("height", c_uint),
        ("dpi", c_uint)
    ]


# 定义 IScreenShotClass 类的函数指针类型（使用 __thiscall 调用约定）
class IScreenShotClass(ctypes.Structure):
    """对应 C++ 中的 IScreenShotClass 接口类"""
    pass


# 定义虚函数表结构
class IScreenShotVtbl(ctypes.Structure):
    """IScreenShotClass 的虚函数表"""
    _fields_ = [
        ("destructor", ctypes.WINFUNCTYPE(None, POINTER(IScreenShotClass))),  # 析构函数
        ("cap", ctypes.WINFUNCTYPE(c_void_p, POINTER(IScreenShotClass))),  # cap() 方法
        ("release", ctypes.WINFUNCTYPE(None, POINTER(IScreenShotClass)))  # release() 方法
    ]


# 完善 IScreenShotClass 结构，包含虚函数表指针
IScreenShotClass._fields_ = [
    ("lpVtbl", POINTER(IScreenShotVtbl))
]

# 定义 CreateScreenShotInstance 函数类型
CreateScreenShotInstanceFunc = ctypes.WINFUNCTYPE(
    POINTER(IScreenShotClass),  # 返回值：IScreenShotClass 指针
    c_uint,  # 参数1：playeridx
    wintypes.DWORD  # 参数2：playerpid
)


class LD:
    """LD 模拟器控制器，实现截图功能"""

    def __init__(self, config: Config,parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config = config
        self.dll_handle = None  # ldopengl64.dll 句柄
        self.screenshot_instance = None  # IScreenShotClass 实例
        self.emu_info = LDLIST2()  # 模拟器信息

    def init(self):
        self.set_ld_path()
        self.connect_emu()

    def __del__(self):
        """析构函数，释放资源"""
        self.release()

    def set_ld_path(self) -> bool:
        """设置 LD 模拟器安装路径"""
        if not os.path.exists(self.config.get_config('雷电安装路径')):
            self.logger.warning(f"LD 模拟器路径不存在: {self.config.get_config('雷电安装路径')}")
            return False

        # 检查 ldconsole.exe 是否存在
        ldconsole_path = os.path.join(self.config.get_config('雷电安装路径'), "ldconsole.exe")
        if not os.path.exists(ldconsole_path):
            self.logger.warning(f"未找到 ldconsole.exe: {ldconsole_path}")
            return False
        return True

    def get_emu_list(self) -> List[LDLIST2]:
        """获取所有模拟器实例列表（通过 ldconsole.exe list2 命令）"""
        if not self.config.get_config('雷电安装路径'):
            self.logger.warning("请先设置 LD 模拟器路径")
            return []

        ldconsole_path = os.path.join(self.config.get_config('雷电安装路径'), "ldconsole.exe")
        cmd = f'"{ldconsole_path}" list2'

        try:
            # 执行命令并获取输出
            output = self._execute_command(cmd)
            if not output:
                self.logger.error("获取模拟器列表失败")
                return []

            # 解析输出为 LDLIST2 列表
            return self._parse_emu_list(output)

        except Exception as e:
            self.logger.error(f"获取模拟器列表出错: {str(e)}")
            return []

    def connect_emu(self) -> bool:
        """连接到指定索引的模拟器实例"""
        # 获取模拟器列表
        emu_list = self.get_emu_list()
        if not emu_list:
            return False

        # 查找指定索引的模拟器
        target_emu = None
        for emu in emu_list:
            if emu.index == self.config.get_config('雷电实例索引'):
                target_emu = emu
                self.logger.info(f"找到模拟器: 名称={target_emu.name.decode('gbk')}, PID={target_emu.playerpid}, 分辨率={target_emu.width}x{target_emu.height}")
                break
            else:
                self.logger.info(f"存在模拟器: 名称={emu.name.decode('gbk')}, PID={emu.playerpid}, 分辨率={emu.width}x{emu.height}")

        if not target_emu:
            self.logger.warning(f"未找到索引为 {self.config.get_config('雷电实例索引')} 的模拟器实例")
            return False

        self.emu_info = target_emu

        # 加载 ldopengl64.dll
        if not self._load_ld_opengl_dll():
            return False

        # 创建截图实例
        if not self._create_screenshot_instance():
            return False

        return True

    def screencap(self) -> Optional[np.ndarray]:
        """捕获当前模拟器屏幕截图"""
        if not self.screenshot_instance:
            self.logger.warning("未连接到模拟器，请先调用 connect_emu 方法")
            return None

        # 调用 cap() 方法获取像素数据
        try:
            # 获取虚函数表中的 cap 方法
            cap_func = self.screenshot_instance.contents.lpVtbl.contents.cap
            pixels = cap_func(self.screenshot_instance)

            if not pixels:
                self.logger.warning("截图失败，返回空指针")
                return None

            # 转换像素数据为 OpenCV 图像（BGR 格式，3通道）
            width = self.emu_info.width
            height = self.emu_info.height
            buffer_size = width * height * 3  # 3字节 per pixel (BGR)

            # 将像素指针转换为字节数组
            pixels_array = ctypes.cast(
                pixels,
                POINTER(c_ubyte * buffer_size)
            ).contents

            # 转换为 numpy 数组并重塑为图像尺寸
            img = np.frombuffer(pixels_array, dtype=np.uint8)
            img = img.reshape((height, width, 3))
            if img.shape[:2] < (900, 1600):
                img = cv2.resize(img, (1600, 900), interpolation=cv2.INTER_CUBIC)
            elif img.shape[:2] > (900, 1600):
                img = cv2.resize(img, (1600, 900), interpolation=cv2.INTER_AREA)
            # 垂直翻转图像（与 C++ 代码一致）
            img = cv2.flip(img, 0)

            return img

        except Exception as e:
            self.logger.error(f"截图出错: {str(e)}")
            return None

    def release(self) -> None:
        """释放资源"""
        # # 调用 release() 方法释放截图实例
        # if self.screenshot_instance:
        #     try:
        #         release_func = self.screenshot_instance.contents.lpVtbl.contents.release
        #         release_func(self.screenshot_instance)
        #     except Exception as e:
        #         self.logger.error(f"释放截图实例出错: {str(e)}")
        #     self.screenshot_instance = None

        # 不需要手动释放 DLL，Python 会自动处理
        self.dll_handle = None

    def _load_ld_opengl_dll(self) -> bool:
        """加载 ldopengl64.dll 并获取函数地址"""
        dll_path = os.path.join(self.config.get_config('雷电安装路径'), "ldopengl64.dll")
        if not os.path.exists(dll_path):
            self.logger.warning(f"未找到 ldopengl64.dll: {dll_path}")
            return False

        try:
            # 加载 DLL
            self.dll_handle = ctypes.WinDLL(dll_path)
            if not self.dll_handle:
                self.logger.warning(f"加载 DLL 失败: {dll_path}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"加载 ldopengl64.dll 出错: {str(e)}")
            return False

    def _create_screenshot_instance(self) -> bool:
        """创建 IScreenShotClass 实例"""
        if not self.dll_handle:
            self.logger.warning("DLL 未加载，请先调用 _load_ld_opengl_dll")
            return False
        create_func = CreateScreenShotInstanceFunc(
            ("CreateScreenShotInstance", self.dll_handle)
        )
        # 调用函数创建实例
        self.screenshot_instance = create_func(
            self.emu_info.index,
            self.emu_info.playerpid
        )
        if not self.screenshot_instance:
            self.logger.warning("创建 IScreenShotClass 实例失败")
            return False

        self.logger.debug("IScreenShotClass 实例创建成功")
        return True

    def _execute_command(self, cmd: str) -> str:
        """执行命令并返回输出结果"""
        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
        sa.lpSecurityDescriptor = None
        sa.bInheritHandle = True

        h_read, h_write = wintypes.HANDLE(), wintypes.HANDLE()
        if not CreatePipe(ctypes.byref(h_read), ctypes.byref(h_write), ctypes.byref(sa), 0):
            raise Exception(f"创建管道失败，错误码: {ctypes.get_last_error()}")

        # 设置启动信息
        si = STARTUPINFOA()
        si.cb = ctypes.sizeof(STARTUPINFOA)
        si.hStdOutput = h_write
        si.hStdError = h_write
        si.dwFlags |= 0x00000100  # STARTF_USESTDHANDLES

        pi = PROCESS_INFORMATION()

        # 执行命令
        if not CreateProcessA(
                None,
                ctypes.create_string_buffer(cmd.encode('gbk')),
                None,
                None,
                True,
                0,
                None,
                None,
                ctypes.byref(si),
                ctypes.byref(pi)
        ):
            CloseHandle(h_read)
            CloseHandle(h_write)
            raise Exception(f"创建进程失败，错误码: {ctypes.get_last_error()}")

        # 关闭写入句柄
        CloseHandle(h_write)

        # 读取输出
        buffer = create_string_buffer(4096)
        bytes_read = wintypes.DWORD()
        output = []

        while ReadFile(h_read, buffer, ctypes.sizeof(buffer) - 1, ctypes.byref(bytes_read), None):
            if bytes_read.value == 0:
                break
            output.append(buffer.raw[:bytes_read.value])

        # 等待进程结束
        WaitForSingleObject(pi.hProcess, -1)  # INFINITE

        # 关闭句柄
        CloseHandle(h_read)
        CloseHandle(pi.hProcess)
        CloseHandle(pi.hThread)

        # 解码输出（假设使用 GBK 编码）
        return b''.join(output).decode('gbk', errors='replace')

    def _parse_emu_list(self, output: str) -> List[LDLIST2]:
        """解析 ldconsole.exe list2 输出为 LDLIST2 列表"""
        emu_list = []
        lines = output.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                # 解析每行数据，格式: index,name,topWnd,bndWnd,sysboot,playerpid,vboxpid,width,height,dpi
                parts = line.split(',')
                if len(parts) != 10:
                    continue

                emu = LDLIST2()
                emu.index = int(parts[0])
                emu.name = parts[1].encode('gbk')[:63]  # 确保不超过 64 字节
                emu.topWnd = int(parts[2])
                emu.bndWnd = int(parts[3])
                emu.sysboot = bool(int(parts[4]))
                emu.playerpid = int(parts[5])
                emu.vboxpid = int(parts[6])
                emu.width = int(parts[7])
                emu.height = int(parts[8])
                emu.dpi = int(parts[9])

                emu_list.append(emu)

            except Exception as e:
                self.logger.error(f"解析模拟器信息失败: {line}, 错误: {e}")
                continue

        return emu_list
