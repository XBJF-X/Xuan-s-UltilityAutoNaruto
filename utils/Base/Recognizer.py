import logging
import time
from typing import Tuple, List, Dict

import cv2
import numpy as np

from StaticFunctions import get_real_path, cv_imread
from utils.Base.Enums import MatchType
from utils.Base.Scene.Element import Element
from utils.Base.Scene.Scene import Scene
from utils.Base.Scene.SceneGraph import SceneGraph


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
    def __init__(self, scene_graph: SceneGraph, parent_logger):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("识别器")
        else:
            self.logger = parent_logger.getChild("识别器")
        self.scene_graph = scene_graph

    def scene(self, scene_img, bool_debug=True):
        """
        结合Alpha通道的模板匹配，忽略透明区域

        Args:
            scene_img(np.ndarray): 需要识别的图像
            bool_debug(bool): 是否回报日志

        Returns:
            (Scene):检测到的场景实例
        """
        best_match_id = None
        best_match_score = 0.0
        for scene_id, scene in self.scene_graph.scenes.items():
            if scene.gray is None:
                continue

            # 执行模板匹配
            matched, match_score = self._single_template_match(
                scene_img, scene, bool_debug
            )

            # 更新最佳匹配
            if matched and match_score > best_match_score:
                best_match_id = scene_id
                best_match_score = match_score

                # 如果匹配度非常高，提前终止
                if match_score > 0.95:  # 可调阈值
                    if bool_debug:
                        self.logger.debug(f"提前终止: {scene_id}匹配度过高({match_score:.2f})")
                    break

        # 4. 结果验证
        if best_match_id and best_match_score >= self.scene_graph.scenes.get(best_match_id).threshold:
            if bool_debug:
                self.logger.info(f"匹配成功: {best_match_id} ({best_match_score:.4f})")
            return self.scene_graph.scenes.get(best_match_id)
        return "未知场景"

        start = time.perf_counter()
        color_scores = []
        for scene_id, scene in self.scene_graph.scenes.items():
            scene_rgb = self._rgb_average(scene_img, scene.mask)
            # 计算颜色相似度（欧氏距离的倒数）
            color_dist = np.sqrt(
                (scene_rgb[0] - scene.rgb[0]) ** 2 +
                (scene_rgb[1] - scene.rgb[1]) ** 2 +
                (scene_rgb[2] - scene.rgb[2]) ** 2
            )
            # 距离越小越相似，转换为相似度分数（0-1）
            color_score = 1 / (1 + color_dist)
            color_scores.append((scene_id, color_score))
        # 按颜色相似度降序排序
        color_scores.sort(key=lambda x: x[1], reverse=True)

        # 3. 按颜色相似度顺序进行模板匹配
        best_match_id = None
        best_match_score = 0.0

        for scene_id, color_score in color_scores:
            scene = self.scene_graph.scenes.get(scene_id)

            # 如果颜色相似度已经很低，提前终止
            if color_score < 0.3 and best_match_score > 0:  # 可调阈值
                if bool_debug:
                    self.logger.debug(f"提前终止: {scene_id}颜色相似度过低({color_score:.2f})")
                break

            # 执行模板匹配
            matched, match_score = self._single_template_match(
                scene_img, scene, bool_debug
            )

            # 更新最佳匹配
            if matched and match_score > best_match_score:
                best_match_id = scene_id
                best_match_score = match_score

                # 如果匹配度非常高，提前终止
                if match_score > 0.95:  # 可调阈值
                    if bool_debug:
                        self.logger.debug(f"提前终止: {scene_id}匹配度过高({match_score:.2f})")
                    break

        # 4. 结果验证
        if best_match_id and best_match_score >= self.scene_graph.scenes.get(best_match_id).threshold:
            if bool_debug:
                self.logger.info(f"匹配成功: {best_match_id} ({best_match_score:.4f})")
            return best_match_id, best_match_score

        if bool_debug:
            self.logger.warning("未找到匹配场景")
        return None, 0.0

    def _single_template_match(self, scene_img, scene, bool_debug=True):
        """单个模板匹配实现"""
        try:
            # 灰度转换
            scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY)

            # 带掩码的模板匹配
            result = cv2.matchTemplate(
                scene_gray,
                scene.gray,
                method=cv2.TM_CCOEFF_NORMED,
                mask=scene.mask
            )

            result = np.nan_to_num(result, nan=-1.0, posinf=-1.0, neginf=-1.0)

            # 获取最大匹配值
            _, max_val, _, _ = cv2.minMaxLoc(result)

            # if bool_debug:
            #     self.logger.debug(f"[{scene.id}] 匹配度: {max_val:.4f}")

            return max_val >= scene.threshold, max_val

        except Exception as e:
            self.logger.error(f"模板匹配出错[{scene.id}]: {str(e)}")
            return False, 0.0

    def scene_match(self, scene_img, template, bool_debug=True):
        """
        只对传入场景进行匹配，为了与scene区分
        Args:
            scene_img:
            template(Scene):
            bool_debug:

        Returns:

        """
        template_img = template.gray
        mask = template.mask
        threshold = template.threshold
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        # 执行模板匹配（添加异常捕获）
        try:
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
        if bool_debug:
            self.logger.debug(f"[{template.id}]匹配结果统计：最大值={max_val:.2f}")
        if max_val >= threshold:
            return True, max_val
        else:
            return False, 0.0

    def element_match(self, scene_img, template, bool_debug=True):
        """
        在场景图中匹配模板元素，忽略模板的透明像素（Alpha=0区域），支持多目标和去重

        Args:
            scene_img(np.ndarray): 场景图像（BGR格式的numpy数组，如截图）
            template(Element): 模板图像名称（str）
            bool_debug(bool): 是否回报日志

        Returns:
            List[Tuple[int, int, int, int]]
            目标位置列表，每个元素为(x1, y1, x2, y2)，表示匹配区域的左上角和右下角坐标
        """
        if template.match_type == MatchType.SIFT:
            return self.sift_match(template, scene_img)
        else:
            return self.template_match(template, scene_img, bool_debug)

    def sift_match(self, template, scene_img, ratio=0.75):
        min_match_ratio = template.threshold
        # 1. 读取图像
        template_gray = template.gray
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)

        # 处理ROI
        roi = template.roi
        if roi:
            x, y, w_roi, h_roi = roi
            scene_gray_roi = scene_gray[y:y + h_roi, x:x + w_roi]
        else:
            x, y = 0, 0  # 如果没有ROI，偏移量为0
            scene_gray_roi = scene_gray

        h, w = template_gray.shape[:2]  # 模板尺寸

        # 2. 初始化SIFT检测器
        sift = cv2.SIFT_create()

        # 3. 检测特征点并计算描述符（计时）
        start_time = time.perf_counter()
        kp1, des1 = sift.detectAndCompute(template_gray, None)  # 模板特征
        kp2, des2 = sift.detectAndCompute(scene_gray_roi, None)  # 场景特征（在ROI区域内）
        feature_time = time.perf_counter() - start_time

        # 计算最小匹配点数（基于模板特征数量的比例）
        num_template_features = len(kp1)
        # 确保至少有4个匹配点（单应性矩阵计算的最小要求）
        min_good_matches = max(4, int(num_template_features * min_match_ratio))
        self.logger.debug(f"[{template.id}] 模板特征数: {num_template_features}, 所需最小匹配: {min_good_matches}")

        # 如果没有足够的特征点或描述符，直接返回空结果
        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            self.logger.debug(f"[{template.id}] 特征点不足: 模板={len(kp1) if kp1 else 0}, 场景={len(kp2) if kp2 else 0}")
            return []

        # 4. 匹配特征点（使用FLANN快速匹配器）
        start_time = time.perf_counter()
        # FLANN参数设置
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=70)  # 检查次数越多，匹配越准但越慢

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)  # k=2返回每个特征的两个最佳匹配
        match_time = time.perf_counter() - start_time

        # 5. 应用Lowe's比例测试过滤误匹配
        good_matches = []
        for m, n in matches:
            if m.distance < ratio * n.distance:  # 最佳匹配距离远小于次佳匹配
                good_matches.append(m)
        self.logger.debug(f"[{template.id}] 有效匹配点数：{len(good_matches)}")

        if len(good_matches) >= min_good_matches:
            # 提取匹配点坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # 计算单应性矩阵（通过RANSAC过滤异常值）
            H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if H is None:
                self.logger.debug(f"[{template.id}] 无法计算单应性矩阵")
                return []

            # 模板四个角点映射到场景图
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, H)  # 场景图中匹配区域的四个角点

            # 将ROI区域内的坐标转换为原图坐标
            for i in range(len(dst)):
                dst[i][0][0] += x  # x坐标加上ROI的x偏移
                dst[i][0][1] += y  # y坐标加上ROI的y偏移

            corners_2d = [point[0] for point in dst]  # 格式：[(x1,y1), (x2,y2), (x3,y3), (x4,y4)]

            # 计算最小和最大坐标（确定边界框）
            x_coords = [p[0] for p in corners_2d]
            y_coords = [p[1] for p in corners_2d]
            # 框的边界坐标
            location = (int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords)))
            return [location]
        else:
            return []

    def template_match(self, template: Element, scene_img, bool_debug: bool = True):
        template_img = template.gray
        mask = template.mask
        threshold = template.threshold
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        x, y, w, h = [0, 0, 1600, 900]
        # 执行模板匹配（添加异常捕获）
        try:
            roi = template.roi
            if roi:
                x, y, w, h = roi
                scene_gray = scene_gray[y:y + h, x:x + w]
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
        if bool_debug:
            self.logger.debug(f"[{template.id}]匹配结果统计：最大值={max_val:.2f}")
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
            (conf, int(x + dx), int(y + dy), int(x + dx + w), int(y + dy + h))
            for dx, dy, conf in zip(locations[1], locations[0], confidences)
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

    def _rgb_average(self, img, mask=None):
        """
        计算图像在掩码有效区域内的RGB平均颜色

        参数:
            img:
            mask: 外部掩码（可选），若无则使用图像自带的alpha通道

        返回:
            (r, g, b) 平均颜色元组，出错返回None
        """
        try:
            # 分离通道：OpenCV默认BGR(A)格式
            channels = cv2.split(img)
            b, g, r = channels[0:3]  # 提取BGR通道

            # 确定掩码
            if mask is not None:
                # 使用外部传入的掩码
                final_mask = mask
            elif img.shape[2] == 4:
                # 使用图像的alpha通道作为掩码
                _, final_mask = cv2.threshold(channels[3], 1, 255, cv2.THRESH_BINARY)
            else:
                # 无掩码时使用全白掩码
                final_mask = np.ones_like(b) * 255

            # 确保掩码是二值单通道
            if final_mask.ndim > 2:
                final_mask = cv2.cvtColor(final_mask, cv2.COLOR_BGR2GRAY)

            # 计算掩码区域内的平均颜色
            masked_pixels = final_mask > 0
            r_avg = int(np.mean(r[masked_pixels]))
            g_avg = int(np.mean(g[masked_pixels]))
            b_avg = int(np.mean(b[masked_pixels]))

            return r_avg, g_avg, b_avg

        except Exception as e:
            self.logger.error(f"计算平均颜色时出错: {str(e)}")
            return None


if __name__ == "__main__":
    rg = Recognizer(SceneGraph(get_real_path("refactor_src/Template/Scene")))
    img = cv_imread(r"F:\PyProject\DailyQuestsHelper\image\2025-08-01_07-24-49.069996.png")
    print(rg.scene_match(img, True))
