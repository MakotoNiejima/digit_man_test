"""
接口层数据约束：遵循方：你（服务端）和前端
前端json字符串----》接收前端数据 ------- 业务层可以逻辑使用
"""
from dataclasses import field

from pydantic import BaseModel

from atguigu.domain.messages import ChatHistoryMessage


class ChatObject(BaseModel) :
	id: str
	type: str
	title: str | None = None
	attributes: dict = {}


class ChatRequest(BaseModel) :
	sender_id: str
	text: str | None = None
	object: ChatObject | None = None


class ChatResponse(BaseModel) :
	sender_id: str
	message_id: str
	messages: list


class ChatBotMessage(BaseModel) :
	text: str | None
	object: ChatObject | None


class ChatMessageResponse(BaseModel) :
	sender_id: str
	messages: list[ChatHistoryMessage]


class AvatarSessionResponse(BaseModel) :
	"""前端 lm-avatar-chat-sdk 初始化所需会话 JSON。"""
	sessionId: str
	rtcParams: dict = {}
	avatarAssets: dict = {}
