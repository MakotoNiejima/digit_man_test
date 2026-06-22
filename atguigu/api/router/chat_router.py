import uuid

from fastapi import APIRouter, Depends

from atguigu.api.dependency import DialogueServiceDep
from atguigu.api.schema import ChatRequest, ChatResponse, ChatBotMessage, ChatObject
from atguigu.domain.messages import ProcessResult, UserMessage, MessageType
from atguigu.domain.state import FocusedObject
from atguigu.services.dialogue_service import DialogueService

router = APIRouter()

@router.get("/hello")
async def hello():
	return {"message": "Hello World"}

@router.post("/api/chat",response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest,
                        dialogue_service: DialogueServiceDep,
                        )->ChatResponse:
	user_message = _build_user_message(chat_request)
	process_result: ProcessResult = await dialogue_service.hand_dialogue(user_message)
	return _build_chat_message(process_result)

def _build_user_message(chat_request: ChatRequest) -> UserMessage:
	return UserMessage(
		sender_id=chat_request.sender_id,
		message_id=str(uuid.uuid4()),
		type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
		text=chat_request.text,
		object=FocusedObject(
			id=chat_request.object.id,
			type=chat_request.object.type,
			title=chat_request.object.title,
			attributes=chat_request.object.attributes,
		) if chat_request.object else None,
	)

def _build_chat_message(process_result: ProcessResult)->ChatResponse:
	return ChatResponse(
		sender_id=process_result.sender_id,
		message_id=process_result.message_id,
		messages=[
			ChatBotMessage(
				text=bot_message.text,
				object=ChatObject(
					id=bot_message.object.id,
					type=bot_message.object.type,
					title=bot_message.object.title,
					attributes=bot_message.object.attributes,
				)if bot_message.object else None,
			)for bot_message in process_result.messages
		]
	)
