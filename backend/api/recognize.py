"""场景识别 API 路由"""
from fastapi import APIRouter, HTTPException, UploadFile, File

from backend.services.recognizer_service import RecognizerService

router = APIRouter()
_recognizer_service = RecognizerService()


@router.post("/recognize")
async def recognize_scene(file: UploadFile = File(...)):
    """上传截图并识别场景"""
    try:
        image_bytes = await file.read()
        scene_name = _recognizer_service.recognize(image_bytes)
        return {"scene": scene_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")