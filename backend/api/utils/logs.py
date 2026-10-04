"""历史日志恢复端点（`GET /api/utils/log-history`）。

阶段 3.4：由 backend/api/utils.py 拆分而来；阶段 3.4（后半）：路由只做参数映射，
读取/解析/汇总逻辑下沉到 `backend/services/log_service.py`。

模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import logging

from backend.services.log_service import read_log_history

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


# ============================================================
# 1. 历史日志恢复
# ============================================================
@router.get("/log-history")
def get_log_history(config_id: str = "", limit: int = 500):
    """读取历史日志文件供前端刷新/重连后恢复展示

    - config_id 为空或 "__global__"：读取 Main.log*，仅返回无归属(config_id=="")的程序日志
    - config_id = Config_N：读取 log/<用户名>/<日期>/Xuan.log*(轮转) + Main.log 中该配置行
    """
    return read_log_history(config_id, limit)
