import logging
import os
import signal
import subprocess
import time
from threading import Timer

import cv2
import numpy as np
from requests import Session

from utils.Base.Config import Config
from StaticFunctions import get_real_path


class DroidCastRaw:
    adb_command = ['adb']

    class DeviceConnect(Exception):
        pass

    class PushApk(Exception):
        pass

    class StartService(Exception):
        pass

    class CheckService(Exception):
        pass

    class ForwardPort(Exception):
        pass

    def __init__(self, config: Config,parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config = config
        self.serial = config.get_config("串口")  # 设备序列号
        self.device_port = 8080  # 设备上的服务端口
        self.pc_port = 53516  # 电脑上的转发端口
        self.session = Session()
        self.service_thread = None

    def init(self):
        signal.signal(signal.SIGINT, self._handler)
        logging.basicConfig(level=logging.DEBUG)

        try:
            self._cleanup_ports()
            self._identify_device()
            self._push_apk()
            self._start_droidcastraw_service()
            Timer(2, self._forward_port).start()
        except self.DeviceConnect as e:
            self.logger.error(f"设备连接错误：{e}")
        except self.PushApk as e:
            self.logger.error(f"安装包推送错误：{e}")
        except self.ForwardPort as e:
            self.logger.error(f"端口转发错误: {e}")
        except Exception as e:
            self.logger.error(f"未知错误：{e}")

    def _cleanup_ports(self):
        """连接前清理设备和电脑上的端口占用"""
        self.logger.info("开始清理端口资源...")

        # 1. 清除电脑上的ADB端口转发规则
        self.logger.debug(f"清理电脑上的端口转发：tcp:{self.pc_port}")
        return_code, _, stderr = self._run_adb(["forward", "--remove", f"tcp:{self.pc_port}"])
        if return_code != 0 and "not found" not in stderr:
            self.logger.warning(f"清理端口转发失败：{stderr.strip()}")

        # 2. 清除设备上占用目标端口的进程
        self.logger.debug(f"清理设备上占用端口 {self.device_port} 的进程")
        # 通过netstat查找占用端口的进程PID（需要设备支持netstat）
        return_code, output, stderr = self._run_adb([
            "shell", f"netstat -tulnp | grep :{self.device_port} | awk '{{print $7}}' | cut -d'/' -f1"
        ])
        if return_code == 0 and output.strip():
            pids = output.strip().split()
            for pid in pids:
                self._run_adb(["shell", f"kill {pid}"])
                self.logger.debug(f"已终止设备上占用端口的进程：{pid}")
        else:
            self.logger.debug(f"设备端口 {self.device_port} 未被占用或清理失败")

        # 3. 可选：重启ADB服务（解决连接不稳定问题）
        self.logger.debug("重启ADB服务")
        subprocess.run(self.adb_command + ["kill-server"], check=False)
        subprocess.run(self.adb_command + ["start-server"], check=False)

    def _start_droidcastraw_service(self):
        """改进的服务启动方法"""
        # 先清理可能存在的旧进程
        self._run_adb(["shell", "pkill -f DroidCast_raw"])

        # 启动服务并重定向输出到文件
        subprocess.run(self.adb_command + [
            "shell",
            "CLASSPATH=/data/local/tmp/DroidCast_raw-release-1.1.apk",
            "app_process",
            "/",
            "ink.mol.droidcast_raw.Main",
            f"--port={self.device_port}",
            "> /sdcard/droidcast.log 2>&1 &"  # 重定向日志到文件
        ], check=False)
        self.logger.info("DroidCast服务启动命令已执行")

    def _run_adb(self, args, pipe_output=True):
        """执行adb命令，使用全局参数中的设备序列号"""
        if self.serial:
            args = self.adb_command + ['-s', self.serial] + args
        else:
            args = self.adb_command + args

        output = subprocess.PIPE if pipe_output else None
        process = subprocess.Popen(
            [str(arg) for arg in args],
            stdout=output,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def _identify_device(self):
        return_code, output, stderr = self._run_adb(["devices"])
        if return_code != 0:
            raise self.DeviceConnect(f"ADB命令执行失败：{stderr.strip()}")

        self.logger.debug("已连接设备列表：")
        self.logger.debug(output.strip())

        devices = []
        for line in output.strip().split('\n')[1:]:
            if 'device' in line:
                devices.append(line.split()[0])

        if not devices:
            raise self.DeviceConnect("未发现任何在线设备，请确保设备已连接并开启USB调试")

        if self.serial:
            if self.serial not in devices:
                raise self.DeviceConnect(f"指定的设备序列号 {self.serial} 未找到，请检查是否正确")
            self.logger.debug(f"已选择设备：{self.serial}")
        else:
            if len(devices) == 1:
                self.serial = devices[0]
                self.logger.debug(f"自动选择唯一设备：{self.serial}")
            else:
                raise self.DeviceConnect(f"发现多个设备，请传入设备序列号（可选：{', '.join(devices)}）")

    def _push_apk(self):
        apk_local_path = get_real_path("bin/DroidCastRaw/DroidCast_raw-release-1.1.apk")
        return_code, output, stderr = self._run_adb(["push", apk_local_path, "/data/local/tmp/"])
        if return_code != 0:
            raise self.PushApk(f"推送安装包出错：{stderr.strip()}")
        else:
            self.logger.info("推送安装包成功")

    def _forward_port(self):
        return_code, output, stderr = self._run_adb(
            [
                "forward",
                f"tcp:{self.pc_port}",
                f"tcp:{self.device_port}"
            ]
        )
        if return_code != 0:
            raise self.ForwardPort(stderr.strip())
        else:
            self.logger.info(f"转发端口成功：{output}")

    def _handler(self, signum, frame):
        self.logger.debug(f'\n>>> Signal caught: {signum}')
        return_code, _, _ = self._run_adb(["forward", "--remove", f"tcp:{self.pc_port}"])
        self.logger.debug(f">>> adb unforward tcp:{self.pc_port}")
        if self.service_thread and self.service_thread.is_alive():
            self.logger.debug(">>> 等待服务线程结束...")

    def screencap(self):
        time1 = time.perf_counter()
        image = self.session.get(f'http://127.0.0.1:{self.pc_port}/screenshot?width=1600&height=900', timeout=3).content
        time2 = time.perf_counter()
        shape = (900, 1600)
        try:
            arr = np.frombuffer(image, dtype=np.uint16)
            arr = arr.reshape(shape)
        except ValueError as e:
            if len(image) < 500:
                self.logger.warning(f'Unexpected screenshot: {image}')
        time3 = time.perf_counter()
        r = cv2.bitwise_and(arr, 0b1111100000000000)
        r = cv2.convertScaleAbs(r, alpha=0.00390625)
        m = cv2.convertScaleAbs(r, alpha=0.03125)
        cv2.add(r, m, dst=r)

        g = cv2.bitwise_and(arr, 0b0000011111100000)
        g = cv2.convertScaleAbs(g, alpha=0.125)
        m = cv2.convertScaleAbs(g, alpha=0.015625, dst=m)
        cv2.add(g, m, dst=g)

        b = cv2.bitwise_and(arr, 0b0000000000011111)
        b = cv2.convertScaleAbs(b, alpha=8)
        m = cv2.convertScaleAbs(b, alpha=0.03125, dst=m)
        cv2.add(b, m, dst=b)
        time4 = time.perf_counter()
        image = cv2.merge([b, g, r])
        # print(f"接受图像：{(time2 - time1) * 1000}ms")
        # print(f"shape：{(time3 - time2) * 1000}ms")
        # print(f"异或：{(time4 - time3) * 1000}ms")
        # print(f"merge：{(time.perf_counter() - time4) * 1000}ms")

        return image

    def release(self):
        # 释放资源，但是懒得释放了
        pass


if __name__ == "__main__":
    os.environ['PATH'] = os.pathsep.join(["D:/Program Files (x86)/leidian/LDPlayer9",
                                             os.environ.get('PATH', '')])
    d = DroidCastRaw(Config())
    d.init()
    time.sleep(3)
    start = time.perf_counter()
    screen = d.screencap()
    for i in range(100):
        screen = d.screencap()
    print(f"单张耗时：{(time.perf_counter() - start) * 1000 / 100}ms")
