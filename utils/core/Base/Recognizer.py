import logging
import time
from typing import Tuple, List, Dict

import cv2
import numpy as np


def visualize_confidence_heatmap(result, template_name):
    """使用OpenCV绘制置信度热力图"""
    # 将置信度值（范围[-1, 1]）归一化到[0, 255]
    normalized = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # 应用颜色映射（jet色彩方案）
    heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)

    # 添加标题
    cv2.putText(heatmap, f'置信度热力图 - {template_name}',
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return heatmap


class Recognizer:
    def __init__(self, scene_templates: Dict, element_templates: Dict):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scene_templates = scene_templates
        self.element_templates = element_templates

    def scene_match(self, scene_img: np.ndarray, template_name: str) -> Tuple[bool, float]:
        """
        结合Alpha通道的模板匹配，忽略透明区域
        :param scene_img: 场景图（BGR格式，numpy数组）
        :param template_name: 模板图像名称（str）
        :return: (是否匹配成功，匹配成功的置信度)
        """
        # start = time.perf_counter()
        template_data = self.scene_templates[template_name]
        template_img = template_data['GRAY']
        mask = template_data['MASK']
        threshold = template_data['threshold']
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        # 验证scene_img是否为有效的NumPy数组
        if not isinstance(scene_img, np.ndarray) or scene_img.size == 0:
            self.logger.error("场景图像不是有效的NumPy数组或为空")
            return False, 0.0

        if not isinstance(template_img, np.ndarray) or template_img.size == 0:
            self.logger.error("模板图像不是有效的NumPy数组或为空")
            return False, 0.0

        if scene_img is None or template_img is None:
            self.logger.warning("场景或模版为空")
            return False, 0.0

        # 2. 对场景图和模板图进行模板匹配（仅使用非透明区域）
        # 使用归一化相关系数法（适合亮度变化场景）
        result = cv2.matchTemplate(
            scene_gray,
            template_img,
            method=cv2.TM_CCOEFF_NORMED,
            mask=mask
        )

        # 3. 判断最高匹配得分是否超过阈值
        max_score = np.max(result)  # 获取所有位置中的最高匹配得分
        # 检查result的统计信息
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        self.logger.debug(f"[{template_name}]匹配结果统计：最大值={max_val:.2f}")
        # vis_img = visualize_confidence_heatmap(result, template_name)
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 截取前3位毫秒
        # # 构建带时间戳的文件名
        # filename = f"confidence_heat/{template_name}_{timestamp}.png"
        # cv2.imwrite(get_real_path(filename), vis_img)
        # print(f"[SCENE_MATCH]耗时 {(time.perf_counter() - start) * 1000:.2f} ms")
        return max_score >= threshold, max_score  # 超过阈值则认为匹配成功

    def element_match(self, scene_img: np.ndarray, template_name: str) -> List[
        Tuple[int, int, int, int]]:
        """
        在场景图中匹配模板元素，忽略模板的透明像素（Alpha=0区域），支持多目标和去重

        Args:
            scene_img: 场景图像（BGR格式的numpy数组，如截图）
            template_name: 模板图像名称（str）

        Returns:
            目标位置列表，每个元素为(x1, y1, x2, y2)，表示匹配区域的左上角和右下角坐标
        """
        template_data = self.element_templates[template_name]
        if template_data.get('match_way', None) == "SIFT":
            return self.sift_match(template_data, scene_img, template_name)
        else:
            return self.template_match(template_data, scene_img, template_name)

    def sift_match(self, template_data, scene_img, template_name, min_good_matches=10, ratio=0.75):
        # 1. 读取图像
        template_gray = template_data['GRAY']
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        h, w = template_gray.shape[:2]  # 模板尺寸
        # 2. 初始化SIFT检测器
        sift = cv2.SIFT_create()

        # 3. 检测特征点并计算描述符（计时）
        start_time = time.perf_counter()
        kp1, des1 = sift.detectAndCompute(template_gray, None)  # 模板特征
        kp2, des2 = sift.detectAndCompute(scene_gray, None)  # 场景特征
        feature_time = time.perf_counter() - start_time

        # 4. 匹配特征点（使用FLANN快速匹配器）
        start_time = time.perf_counter()
        # FLANN参数设置
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)  # 检查次数越多，匹配越准但越慢

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)  # k=2返回每个特征的两个最佳匹配
        match_time = time.perf_counter() - start_time

        # 5. 应用Lowe's比例测试过滤误匹配
        good_matches = []
        for m, n in matches:
            if m.distance < ratio * n.distance:  # 最佳匹配距离远小于次佳匹配
                good_matches.append(m)
        self.logger.debug(f"[{template_name}] 有效匹配点数：{len(good_matches)}")
        if len(good_matches) >= min_good_matches:
            # 提取匹配点坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # 计算单应性矩阵（通过RANSAC过滤异常值）
            H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # 模板四个角点映射到场景图
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, H)  # 场景图中匹配区域的四个角点
            corners_2d = [point[0] for point in dst]  # 格式：[(x1,y1), (x2,y2), (x3,y3), (x4,y4)]

            # 计算最小和最大坐标（确定边界框）
            x_coords = [p[0] for p in corners_2d]
            y_coords = [p[1] for p in corners_2d]
            # 框的边界坐标
            location = (int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords)))
            return [location]
        else:
            return []

    def template_match(self, template_data, scene_img, template_name):
        template_img = template_data['GRAY']
        mask = template_data['MASK']
        threshold = template_data['threshold']
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        x1, x2, y1, y2 = [0, 0, 0, 0]
        # 执行模板匹配（添加异常捕获）
        try:
            if scene_img.shape[:2] < (900, 1600):
                scene_gray = cv2.resize(scene_gray, (1600, 900), interpolation=cv2.INTER_CUBIC)
            elif scene_img.shape[:2] > (900, 1600):
                scene_gray = cv2.resize(scene_gray, (1600, 900), interpolation=cv2.INTER_AREA)
            roi = template_data.get('roi', None)
            if roi:
                x1, x2, y1, y2 = roi
                scene_gray = scene_gray[y1:y2, x1:x2]
            result = cv2.matchTemplate(
                image=scene_gray,
                templ=template_img,
                method=cv2.TM_CCOEFF_NORMED,
                mask=mask
            )
            # 修复非有限值：将 NaN/Inf 替换为 -1（有效值范围是[-1,1]）
            result = np.nan_to_num(result, nan=-1.0, posinf=-1.0, neginf=-1.0)
        except cv2.error as e:
            self.logger.error(f"模板匹配出错：{e}")
            return []
        # # 检查result的统计信息
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        self.logger.debug(f"[{template_name}]匹配结果统计：最大值={max_val:.2f}")
        # vis_img = visualize_confidence_heatmap(result, template_name)
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 截取前3位毫秒
        # # 构建带时间戳的文件名
        # filename = f"confidence_heat/{template_name}_{timestamp}.png"
        # cv_save(get_real_path(filename), vis_img)

        # 5. 筛选超过阈值的匹配位置，并绑定置信度
        locations = np.where(result >= threshold)  # 所有符合条件的位置
        if len(locations[0]) == 0:
            return []  # 无匹配结果

        # 提取每个匹配位置的置信度值
        confidences = [result[y, x] for y, x in zip(locations[0], locations[1])]
        h, w = template_img.shape[:2]  # 模板的高和宽
        # 构建(置信度, x1, y1, x2, y2)的列表，并按置信度降序排序
        matches_with_conf = [
            (conf, int(x1 + x), int(y1 + y), int(x1 + x + w), int(y1 + y + h))
            for x, y, conf in zip(locations[1], locations[0], confidences)
        ]
        matches_with_conf.sort(reverse=True, key=lambda x: x[0])

        # 提取排序后的框和对应的置信度
        sorted_matches = [(x1, y1, x2, y2) for (conf, x1, y1, x2, y2) in matches_with_conf]
        sorted_confidences = [conf for (conf, x1, y1, x2, y2) in matches_with_conf]  # 新增：提取置信度
        # print(f"[{template_name}]匹配位置（未去重）：{sorted_matches}")
        # print(f"[ELEMENT_MATCH]耗时 {(time.perf_counter() - start) * 1000:.2f} ms")
        # 调用NMS时传入置信度
        return self._non_max_suppression(sorted_matches,
                                         iou_threshold=0.3,
                                         confidences=sorted_confidences)

    @staticmethod
    def _non_max_suppression(boxes: List[Tuple[int, int, int, int]],
                             iou_threshold: float = 0.3,
                             confidences: List[float] = None) -> List[Tuple[int, int, int, int]]:
        """
        去除重叠度高的重复检测框（按置信度优先保留）
        :param boxes: 检测框列表
        :param iou_threshold: IOU阈值
        :param confidences: 每个框对应的置信度（与boxes顺序一致）
        """
        if not boxes:
            return []

        boxes_np = np.array(boxes, dtype=np.float32)
        x1, y1, x2, y2 = boxes_np[:, 0], boxes_np[:, 1], boxes_np[:, 2], boxes_np[:, 3]
        area = (x2 - x1 + 1) * (y2 - y1 + 1)

        # 关键修改：按置信度降序排序（若提供置信度），否则按原顺序
        if confidences is not None:
            indices = np.argsort(np.array(confidences))[::-1]  # 置信度降序索引
        else:
            indices = np.argsort(y2)  # 兼容旧逻辑（无置信度时）

        keep = []
        while indices.size > 0:
            idx = indices[0]  # 取当前置信度最高的框（原逻辑是取最后一个）
            keep.append(boxes[idx])
            indices = indices[1:]  # 移除当前框，处理剩余框

            # 计算与剩余框的IOU
            xx1, yy1 = np.maximum(x1[idx], x1[indices]), np.maximum(y1[idx], y1[indices])
            xx2, yy2 = np.minimum(x2[idx], x2[indices]), np.minimum(y2[idx], y2[indices])
            w, h = np.maximum(0, xx2 - xx1 + 1), np.maximum(0, yy2 - yy1 + 1)
            overlap = (w * h) / (area[idx] + area[indices] - w * h)

            # 保留IOU小于阈值的框
            indices = indices[overlap <= iou_threshold]

        # print(f"匹配位置（去重）：{keep}")
        return keep
