"""场景识别 API 路由"""
from fastapi import APIRouter, HTTPException, UploadFile, File

router = APIRouter()


@router.post("/recognize")
async def recognize_scene(file: UploadFile = File(...)):
    """上传截图并识别场景"""
    raise HTTPException(status_code=501, detail="Not implemented yet")