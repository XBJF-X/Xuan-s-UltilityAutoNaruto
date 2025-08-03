import logging
import dxcam
from utils.Config import Config


class Dxcam:
    """
    通用的截图方案，使用Dxcam库截取全屏，特点：
    1.速度快（单次约5-10ms）
    2.模拟器窗口必须要在屏幕内，不能有任何边界超出
    3.模拟器窗口大小不能变动
    """
    def __init__(self, config: Config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.camera = dxcam.create(device_idx=0, output_color="BGR")  # returns a DXCamera instance on primary monitor
        self.camera.start(target_fps=self.config.get_config('视频流帧率'), video_mode=True)  # Optional argument to capture a region

    def release(self):
        self.camera.release()

    def screencap(self):
        """
        截取模拟器屏幕指定区域的图像，并返回截图数据及时间信息。

        参数:
            region: 截图区域，格式为 (left, top, right, bottom)，坐标基于原始屏幕分辨率。
                - left: 区域左边界像素坐标（int）
                - top: 区域上边界像素坐标（int）
                - right: 区域右边界像素坐标（int）
                - bottom: 区域下边界像素坐标（int）
            resolution: 模拟器屏幕原始分辨率，格式为 (width, height)
                - width: 屏幕宽度（int）
                - height: 屏幕高度（int）

        返回:
            screen: 截取的图像数据（numpy数组，BGR格式）
        """
        try:
            left, top, right, bottom = self.config.get_config('窗口Rect')
            width, height = self.config.get_config('默认分辨率_元组')
            screen = self.camera.get_latest_frame()[bottom - height:bottom, left:left + width]
        except Exception as e:
            self.logger.error(f"截图出错：{str(e)}")
            return None
        return screen
