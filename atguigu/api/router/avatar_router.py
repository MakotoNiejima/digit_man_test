from fastapi import APIRouter
from atguigu.api.schema import AvatarSessionResponse

router = APIRouter()

@router.get("/api/avatar/session")
async def create_session() -> AvatarSessionResponse:
	"""创建数字人云端渲染会话，给前端SDK初始化"""
	data = await avatar.create_chat_session()