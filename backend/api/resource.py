"""资源管理器 API 路由 - 场景/元素的批量 CRUD 接口（新前端专用）

设计目标：
1. 前端初始化一次性全量读取（GET /resource/full），避免逐场景多次请求
2. 场景内元素一次批量读取（GET /resource/scenes/{scene_id}/elements），避免逐元素请求
3. 所有操作均按 UUID id 定位，前端不依赖旧版按名称定位

数据模型语义：
- Scene.id / Element.id 为 UUID 字符串主键
- 元素从属于唯一场景（Element.scene_id 外键必填，1:N）
- SceneEdge 表示场景之间的跳转边（source -> target）
"""
import io
import logging
import re
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response

from backend.tools.resource_db import ResourceDBManager
from backend.tools.resource_model import Scene, Element, SceneEdge
from backend.core.enums import ElementType, MatchType

router = APIRouter()

logger = logging.getLogger("ResourceAPI")

_TEST_SCENE_DIR = str(Path(__file__).resolve().parent.parent.parent / "test_scene")

# Windows 文件名非法字符（含控制字符）
_WINDOWS_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_scene_filename(name: str) -> str:
    """将场景名转换为安全的 Windows 文件名（不含非法字符、去除首尾空格与点）。"""
    safe = _WINDOWS_INVALID_CHARS.sub("_", str(name)).strip(" .")
    return safe or "scene"

# ===== 元素图片 / 场景底图 =====
@router.get("/elements/{element_id}/image")
def get_element_image(element_id: str):
    """获取元素图像（仅存 4 通道 BGRA 原始字节），转为 PNG 返回，供前端 <img> 或 Canvas 显示"""
    element = _db.get_element_by_id(element_id)
    if element is None:
        raise HTTPException(status_code=404, detail="元素不存在")
    raw = getattr(element, "bgra", None)
    if not raw:
        raise HTTPException(status_code=404, detail="该元素没有图像")
    try:
        import numpy as np
        import cv2
        buf = np.frombuffer(bytes(raw), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise HTTPException(status_code=404, detail="图像解码失败")
        ok, png = cv2.imencode(".png", img)
        if not ok:
            raise HTTPException(status_code=500, detail="图像编码失败")
        return Response(content=png.tobytes(), media_type="image/png")
    except ImportError:
        # 无 cv2 时直接返回原始字节（保守降级）
        return Response(content=bytes(raw), media_type="image/png")


@router.post("/elements/{element_id}/image")
async def upload_element_image(element_id: str, file: UploadFile = File(...)):
    """上传/替换元素图像（原始 PNG 字节直接存 bgra，gray/mask 运行时推导），支持 PNG/JPG 等格式"""
    if _db.get_element_by_id(element_id) is None:
        raise HTTPException(status_code=404, detail="元素不存在")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    ok = _db.update_element_by_id(element_id, bgra=data)
    if not ok:
        raise HTTPException(status_code=500, detail="图像保存失败")
    # 同步共享 SceneGraph 单例：重新推导 gray/mask，保证后续匹配/识别用新图
    updated = _db.get_element_by_id(element_id)
    if updated is not None:
        _sync_graph_element(updated, refresh_image=True)
    return {"ok": True}


@router.get("/scenes/{scene_id}/base_image")
def get_scene_base_image(scene_id: str):
    """获取场景底图：优先返回 test_scene/{场景名}.png，不存在则返回 1600x900 白色占位图"""
    from pathlib import Path
    scene = _db.get_scene_by_id(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail="场景不存在")
    candidates = [
        Path(_TEST_SCENE_DIR) / f"{_safe_scene_filename(scene.name)}.png",
        Path(_TEST_SCENE_DIR) / f"{_safe_scene_filename(scene.name)}.jpg",
        Path(_TEST_SCENE_DIR) / f"{_safe_scene_filename(scene.name)}.jpeg",
    ]
    for p in candidates:
        if p.exists():
            # 按实际扩展名返回正确的媒体类型（png → image/png，jpg/jpeg → image/jpeg）
            media_type = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
            return Response(content=p.read_bytes(), media_type=media_type)
    # 未找到底图：生成 1600x900 白色占位图
    try:
        import numpy as np
        import cv2
        img = np.full((900, 1600, 3), 255, dtype=np.uint8)
        ok, png = cv2.imencode(".png", img)
        if ok:
            return Response(content=png.tobytes(), media_type="image/png")
    except ImportError:
        pass
    raise HTTPException(status_code=404, detail="未找到场景底图")


@router.post("/scenes/{scene_id}/base_image")
async def upload_scene_base_image(scene_id: str, file: UploadFile = File(...)):
    """上传/替换场景底图：统一转为 PNG 并保存为 test_scene/{场景名}.png"""
    scene = _db.get_scene_by_id(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail="场景不存在")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    try:
        import numpy as np
        import cv2
        buf = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise HTTPException(
                status_code=400, detail="无法解码为图片，请上传 PNG/JPG 等图片文件")
        ok, png = cv2.imencode(".png", img)
        if not ok:
            raise HTTPException(status_code=500, detail="PNG 编码失败")
        data = png.tobytes()
    except ImportError:
        # 无 cv2 环境时降级：仅接受原始 PNG 字节原样保存（注明影响范围）
        if not data[:8] == b"\x89PNG\r\n\x1a\n":
            raise HTTPException(status_code=400, detail="缺少 cv2 环境，仅支持上传 PNG")
    safe_name = _safe_scene_filename(scene.name)
    dest_dir = Path(_TEST_SCENE_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{safe_name}.png"
    dest.write_bytes(data)
    return {"ok": True, "path": f"test_scene/{safe_name}.png"}

_db = ResourceDBManager()

# 该字段会随元素批量返回，前端无需接收（gray/mask 已废弃，仅 bgra）
_BINARY_FIELDS = ("bgra",)


# ===== 状态 =====
@router.get("/status")
def resource_status():
    """资源管理器状态"""
    return {"status": "ok", "module": "resourcemanager", "ready": True}


# ===== 全量批量读取（前端初始化） =====
@router.get("/full")
def get_full():
    """一次性全量读取所有场景及其元素概要（不含二进制图像），供前端初始化"""
    scenes = _db.get_all_scenes()
    return {
        "scenes": [_scene_detail(s) for s in scenes],
    }


# ===== 场景 CRUD =====
@router.get("/scenes")
def list_scenes():
    """全量场景列表（不包含元素）"""
    scenes = _db.get_all_scenes()
    return {"scenes": [_scene_summary(s) for s in scenes]}


@router.post("/scenes")
def create_scene(payload: dict):
    """新增场景"""
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="场景名称不能为空")
    ok = _db.add_scene(name)
    if not ok:
        raise HTTPException(status_code=400, detail="场景创建失败（可能名称已存在）")
    scene = _db.get_scene_by_name(name)
    return {"scene": _scene_summary(scene) if scene else {"name": name, "id": None}}


@router.put("/scenes/{scene_id}")
def update_scene(scene_id: str, payload: dict):
    """更新场景（支持改名）"""
    new_name = payload.get("name")
    if new_name is not None:
        new_name = str(new_name).strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="场景名称不能为空")
        ok = _db.rename_scene_by_id(scene_id, new_name)
        if not ok:
            raise HTTPException(status_code=400, detail="场景重命名失败（可能名称已存在）")
        _sync_graph_scene_rename(scene_id, new_name)
    return {"ok": True}


@router.delete("/scenes/{scene_id}")
def delete_scene(scene_id: str):
    """删除场景及其全部元素、跳转边"""
    ok = _db.delete_scene_by_id(scene_id)
    if not ok:
        raise HTTPException(status_code=404, detail="场景不存在")
    _unsync_graph_scene(scene_id)
    return {"ok": True}


# ===== 场景跳转边 CRUD =====
@router.get("/edges")
def list_edges():
    """全量场景跳转边"""
    edges = _db.get_all_scene_edges()
    return {
        "edges": [
            {"id": e.id, "source_scene_id": e.source_scene_id, "target_scene_id": e.target_scene_id}
            for e in edges
        ]
    }


@router.post("/edges")
def create_edge(payload: dict):
    """新增场景跳转边"""
    source_scene_id = payload.get("source_scene_id")
    target_scene_id = payload.get("target_scene_id")
    if not source_scene_id or not target_scene_id:
        raise HTTPException(status_code=400, detail="缺少 source_scene_id 或 target_scene_id")
    ok = _db.add_scene_edge_by_ids(str(source_scene_id), str(target_scene_id))
    if not ok:
        raise HTTPException(status_code=400, detail="场景跳转边创建失败")
    return {"ok": True}


@router.delete("/edges")
def delete_edge(payload: dict):
    """删除场景跳转边"""
    source_scene_id = payload.get("source_scene_id")
    target_scene_id = payload.get("target_scene_id")
    if not source_scene_id or not target_scene_id:
        raise HTTPException(status_code=400, detail="缺少 source_scene_id 或 target_scene_id")
    ok = _db.delete_scene_edge_by_ids(str(source_scene_id), str(target_scene_id))
    if not ok:
        raise HTTPException(status_code=404, detail="场景跳转边不存在")
    return {"ok": True}


# ===== TransitionManager 已实现跳转（供前端场景有向图判断边是否实现，未实现的单向边标红） =====
_transitions_cache: list[dict] | None = None


@router.get("/transitions")
def get_implemented_transitions():
    """返回 backend/core/legacy/Scene/TransitionManager.py 中已注册的所有场景跳转 (source, target)。

    仅构建注册表（TransitionManager(None) 只执行 _register_transitions 注册装饰器，
    不依赖 Config/Operationer），返回后可判断 DB 中的每条边是否在 TransitionManager 中实现。
    """
    global _transitions_cache
    if _transitions_cache is None:
        from backend.core.legacy.Scene.TransitionManager import TransitionManager
        tm = TransitionManager(None)
        _transitions_cache = [
            {"source": s, "target": t} for s, t in tm.transition_map.keys()
        ]
    return {"transitions": _transitions_cache}


# ===== 场景内元素批量读取 =====
@router.get("/scenes/{scene_id}/elements")
def list_scene_elements(scene_id: str):
    """一次批量读取场景内全部元素（不含二进制图像）"""
    elements = _db.get_scene_elements_by_id(scene_id)
    return {"scene_id": scene_id, "elements": [_element_summary(e) for e in elements]}


# ===== 元素 CRUD（元素从属于唯一场景） =====
@router.post("/elements")
def create_element(payload: dict):
    """新增元素（必须指定所属场景 scene_id）"""
    scene_id = str(payload.get("scene_id", "")).strip()
    name = str(payload.get("name", "")).strip()
    if not scene_id:
        raise HTTPException(status_code=400, detail="缺少 scene_id")
    if not name:
        raise HTTPException(status_code=400, detail="元素名称不能为空")

    fields = _filter_element_fields(payload, include_name=False)
    element = _db.add_element(scene_id, name, **fields)
    if element is None:
        raise HTTPException(status_code=400, detail="元素创建失败（场景不存在或同名元素已存在）")
    _sync_graph_element(element)
    return {"element": _element_summary(element)}


@router.put("/elements/{element_id}")
def update_element(element_id: str, payload: dict):
    """更新元素字段（名称、类型、阈值、坐标等）"""
    fields = _filter_element_fields(payload)
    if not fields:
        raise HTTPException(status_code=400, detail="没有可更新的字段")
    ok = _db.update_element_by_id(element_id, **fields)
    if not ok:
        raise HTTPException(status_code=404, detail="元素不存在或更新失败")
    # 同步共享 SceneGraph 单例：ROI/阈值/名称等字段变更后识别/匹配必须用新值
    updated = _db.get_element_by_id(element_id)
    if updated is not None:
        _sync_graph_element(updated)
    return {"ok": True}


@router.delete("/elements/{element_id}")
def delete_element(element_id: str):
    """删除元素（从场景中移除）"""
    ok = _db.delete_element_by_id(element_id)
    if not ok:
        raise HTTPException(status_code=404, detail="元素不存在")
    _unsync_graph_element(element_id)
    return {"ok": True}


# ===== 场景/元素匹配与 OCR 识别（编辑器内联验证） =====

def _load_scene_image(scene_id: str):
    """加载场景底图（test_scene/{场景名}.png 等），返回 BGR numpy 数组；无底图抛 400"""
    from backend.core.legacy.Scene.SceneGraph import SceneGraph  # noqa: F401 (确保初始化逻辑一致)
    scene = _db.get_scene_by_id(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail="场景不存在")
    candidates = [
        Path(_TEST_SCENE_DIR) / f"{_safe_scene_filename(scene.name)}.png",
        Path(_TEST_SCENE_DIR) / f"{_safe_scene_filename(scene.name)}.jpg",
        Path(_TEST_SCENE_DIR) / f"{_safe_scene_filename(scene.name)}.jpeg",
    ]
    for p in candidates:
        if p.exists():
            import numpy as np
            import cv2
            img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if img is not None:
                if img.ndim == 3 and img.shape[-1] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return img
    raise HTTPException(status_code=400, detail="场景不存在底图（test_scene/{场景名}.png），无法执行匹配/识别")


# ===== 共享 Recognizer 单例 =====
# 复用全局共享 SceneGraph + 共享 OnnxOcr，避免每次「执行匹配/OCR」请求
# 重新解码全部元素图、重新加载 OCR 模型（峰值内存可达 ~200MB）。
_recognizer_singleton = None


def _get_recognizer():
    """获取模块级共享 Recognizer（惰性构建，线程安全由 GIL + 幂等赋值保证）。"""
    global _recognizer_singleton
    if _recognizer_singleton is None:
        from backend.core.legacy.Recognizer import Recognizer
        from backend.services.scheduler_service import get_shared_scene_graph
        _recognizer_singleton = Recognizer(get_shared_scene_graph())
    return _recognizer_singleton


@router.post("/scenes/{scene_id}/match")
def match_scene(scene_id: str):
    """场景执行匹配：加载底图并调用 recognizer.scene() 识别当前底图属于哪个场景"""
    scene = _db.get_scene_by_id(scene_id)
    if scene is None:
        raise HTTPException(status_code=404, detail="场景不存在")
    scene_img = _load_scene_image(scene_id)
    recognizer = _get_recognizer()
    try:
        recognized = recognizer.scene(scene_img, bool_debug=False)
        recognized_name = recognized.name if hasattr(recognized, "name") else str(recognized)
        return {
            "ok": True,
            "scene_id": scene_id,
            "scene_name": scene.name,
            "recognized": recognized_name,
            "matched": recognized_name == scene.name,
        }
    except Exception as e:
        return {"ok": False, "matched": False, "error": str(e)}


def _find_element_in_graph(recognizer, element_id: str):
    """从 recognizer.scene_graph 中按 id 查找元素（SceneGraph 已预处理 gray/mask）"""
    for scene in recognizer.scene_graph.scenes.values():
        for e in scene.elements:
            if e.id == element_id:
                return e
    return None


# ===== 共享 SceneGraph 单例同步 =====
# 共享 SceneGraph 首次构建时缓存了全部 Element 内存对象（含 ROI/阈值/gray/mask）。
# 资源管理器中增删改元素/场景后必须同步该缓存，否则「执行匹配/OCR」仍用旧数据
# （表现为"微调区域保存后识别又返回上次结果"）。
_GRAPH_SYNC_FIELDS = (
    "name", "symbol", "type", "threshold", "ratio_x", "ratio_y",
    "match_type", "roi_x", "roi_y", "roi_width", "roi_height",
    "ocr_min_score", "coordinate_x", "coordinate_y",
)


def _invalidate_scene_element_dict(scene):
    """失效 Scene.element_dict 的 cached_property 缓存（改名/增删元素后需重建）"""
    try:
        if "element_dict" in scene.__dict__:
            del scene.__dict__["element_dict"]
    except Exception:
        pass


def _refresh_graph_element_image(target, new_bgra_bytes):
    """IMG 元素 bgra 变更后重新推导 gray/mask（与 SceneGraph.__init__ 一致）"""
    if not new_bgra_bytes:
        return
    try:
        import numpy as np
        import cv2
        buf = np.frombuffer(bytes(new_bgra_bytes), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if img is None:
            return
        object.__setattr__(target, "bgra", np.ascontiguousarray(img))
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.uint8)
        object.__setattr__(target, "gray", gray)
        if img.shape[-1] == 4:
            mask = (img[:, :, 3] > 0).astype(np.uint8) * 255
        else:
            mask = np.ones_like(gray, dtype=np.uint8) * 255
        object.__setattr__(target, "mask", mask)
    except Exception as e:
        logger.warning(f"刷新 SceneGraph 元素图像失败: {e}")


def _sync_graph_element(updated: Element, refresh_image: bool = False):
    """将最新元素字段同步到共享 SceneGraph 单例。

    - 共享 SceneGraph 为模块级单例，首次构建时缓存全部元素内存对象；
    - 元素在资源管理器中更新后不同步，识别/匹配仍用旧 ROI/阈值；
    - refresh_image=True（图片上传）时从 bgra 重新推导 gray/mask。
    """
    try:
        from backend.services.scheduler_service import get_shared_scene_graph
        graph = get_shared_scene_graph()
    except Exception:
        return
    scene = next((s for s in graph.scenes.values() if s.id == updated.scene_id), None)
    if scene is None:
        return
    target = next((e for e in scene.elements if e.id == updated.id), None)
    if target is None:
        # 新建元素首次同步：直接追加
        scene.elements.append(updated)
        if updated.type == ElementType.IMG and getattr(updated, "bgra", None):
            _refresh_graph_element_image(updated, getattr(updated, "bgra", None))
        target = updated
    else:
        for f in _GRAPH_SYNC_FIELDS:
            try:
                setattr(target, f, getattr(updated, f))
            except Exception:
                pass
        if refresh_image:
            _refresh_graph_element_image(target, getattr(updated, "bgra", None))
    _invalidate_scene_element_dict(scene)


def _unsync_graph_element(element_id: str):
    """从共享 SceneGraph 单例移除元素（元素删除后）"""
    try:
        from backend.services.scheduler_service import get_shared_scene_graph
        graph = get_shared_scene_graph()
    except Exception:
        return
    for scene in graph.scenes.values():
        before = len(scene.elements)
        scene.elements = [e for e in scene.elements if e.id != element_id]
        if len(scene.elements) != before:
            _invalidate_scene_element_dict(scene)
            return


def _sync_graph_scene_rename(scene_id: str, new_name: str):
    """同步共享 SceneGraph 中的场景改名（graph.scenes 以场景名为 key）"""
    try:
        from backend.services.scheduler_service import get_shared_scene_graph
        graph = get_shared_scene_graph()
    except Exception:
        return
    for old_key, s in list(graph.scenes.items()):
        if s.id == scene_id:
            if old_key != new_name:
                del graph.scenes[old_key]
                s.name = new_name
                graph.scenes[new_name] = s
            return


def _unsync_graph_scene(scene_id: str):
    """从共享 SceneGraph 单例移除场景（场景删除后）"""
    try:
        from backend.services.scheduler_service import get_shared_scene_graph
        graph = get_shared_scene_graph()
    except Exception:
        return
    for key, s in list(graph.scenes.items()):
        if s.id == scene_id:
            del graph.scenes[key]
            return


@router.post("/elements/{element_id}/match")
def match_element(element_id: str):
    """元素执行匹配：加载其所属场景底图并对该元素执行 element_match

    注意：必须使用 recognizer.scene_graph 中已推导 gray/mask 的元素对象，
    不能直接用 _db 查询的元素（其 gray/mask 为空导致 AttributeError）。
    """
    element = _db.get_element_by_id(element_id)
    if element is None:
        raise HTTPException(status_code=404, detail="元素不存在")
    if element.type != ElementType.IMG:
        raise HTTPException(status_code=400, detail="仅 IMG 类型元素可执行匹配")
    scene_img = _load_scene_image(element.scene_id)
    recognizer = _get_recognizer()
    graph_element = _find_element_in_graph(recognizer, element_id)
    if graph_element is None:
        return {"ok": False, "matched": False, "error": "SceneGraph 中找不到该元素（可能无 BGRA 图像）"}
    try:
        matches = recognizer.element_match(scene_img, graph_element, bool_debug=False)
        return {
            "ok": True,
            "matched": len(matches) > 0,
            "count": len(matches),
            "positions": [[int(a), int(b), int(c), int(d)] for a, b, c, d in matches[:10]],
        }
    except Exception as e:
        return {"ok": False, "matched": False, "error": str(e)}


@router.post("/elements/{element_id}/ocr")
def ocr_element(element_id: str):
    """元素执行 OCR 识别：加载其所属场景底图，对该 OCR 元素的 ROI 区域执行 area_ocr"""
    element = _db.get_element_by_id(element_id)
    if element is None:
        raise HTTPException(status_code=404, detail="元素不存在")
    if element.type != ElementType.OCR_AREA:
        raise HTTPException(status_code=400, detail="仅 OCR 区域类型元素可执行识别")
    scene_img = _load_scene_image(element.scene_id)
    recognizer = _get_recognizer()
    # OCR 识别仅依赖 ROI/ocr_min_score 等标量字段（不需要 gray/mask），直接用数据库最新
    # 元素对象，避免共享 SceneGraph 单例缓存旧 ROI 导致"微调区域保存后识别结果不变"。
    try:
        results = recognizer.area_ocr(scene_img, element, bool_debug=False)
        return {
            "ok": True,
            "results": [
                {"text": text, "box": [int(v) for v in box]}
                for text, box, _score in results
            ],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ===== 内部序列化工具 =====

def _scene_summary(s: Scene) -> dict:
    return {"id": s.id, "name": s.name}


def _scene_detail(s: Scene) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "elements": [_element_summary(e) for e in s.elements],
    }


def _element_summary(e: Element) -> dict:
    return {
        "id": e.id,
        "name": e.name,
        "scene_id": e.scene_id,
        "symbol": e.symbol,
        "element_type": int(e.type.value if hasattr(e.type, "value") else e.type),
        "match_type": int(e.match_type.value if hasattr(e.match_type, "value") else e.match_type),
        "threshold": e.threshold,
        "ratio_x": e.ratio_x,
        "ratio_y": e.ratio_y,
        "roi_x": e.roi_x,
        "roi_y": e.roi_y,
        "roi_width": e.roi_width,
        "roi_height": e.roi_height,
        "ocr_min_score": e.ocr_min_score,
        "coordinate_x": e.coordinate_x,
        "coordinate_y": e.coordinate_y,
    }


def _filter_element_fields(payload: dict, include_name: bool = True) -> dict:
    """从请求体中筛出 Element 的合法字段并做类型转换

    include_name=False 时忽略 name（创建场景元素时 name 已作为独立必填参数传入，
    避免与 add_element(scene_id, name, **fields) 的位置参数冲突）。
    """
    type_map: dict[str, Any] = {}
    if "symbol" in payload:
        type_map["symbol"] = bool(payload["symbol"])
    if "element_type" in payload:
        try:
            type_map["type"] = ElementType(int(payload["element_type"]))
        except (ValueError, TypeError):
            type_map["type"] = ElementType.IMG
    if "match_type" in payload:
        try:
            type_map["match_type"] = MatchType(int(payload["match_type"]))
        except (ValueError, TypeError):
            type_map["match_type"] = MatchType.TEMPLATE
    for field in ("threshold", "ratio_x", "ratio_y", "ocr_min_score"):
        if field in payload and payload[field] is not None:
            type_map[field] = float(payload[field])
    for field in ("roi_x", "roi_y", "roi_width", "roi_height", "coordinate_x", "coordinate_y"):
        if field in payload and payload[field] is not None:
            type_map[field] = int(payload[field])
    if include_name and "name" in payload:
        name = str(payload["name"]).strip()
        if name:
            type_map["name"] = name

    allowed = set(Element.__fields__) - {"id", "scene_id", "created_at", "updated_at"}
    return {k: v for k, v in type_map.items() if k in allowed}