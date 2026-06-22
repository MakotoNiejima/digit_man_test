from enum import Enum
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


# 枚举值防止手输输错
class MessageType(Enum) :
	TEXT = "text"
	OBJECT = "object"


@dataclass(slots=True)
class FocusedObject :
	id: str
	type: str
	title: str | None = None
	attributes: dict = field(default_factory=dict)

	def to_dict(self) -> dict :
		return {
			"id" : self.id,
			"type" : self.type,
			"title" : self.title,
			"attributes" : dict(self.attributes)
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "FocusedObject" :
		return cls(
			id=data['id'],
			type=data["type"],
			title=data.get("title"),
			attributes=dict(data.get("attributes")))

@dataclass(slots=True)
class UserMessage :
	"""
	用户角色的消息
	"""
	sender_id: str
	message_id: str
	type: MessageType
	text: str | None = None
	object: FocusedObject | None = None

	def to_dict(self) -> dict :
		return {
			"sender_id" : self.sender_id,
			"message_id" : self.message_id,
			"type" : self.type.value,
			"text" : self.text,
			"object" : self.object.to_dict() if self.object else None
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "UserMessage" :
		return cls(
			sender_id=data["sender_id"],
			message_id=data["message_id"],
			type=MessageType(data["type"]),
			text=data.get("text"),
			object=FocusedObject.from_dict(data["object"]) if data.get("object") else None
		)

@dataclass(slots=True)
class BotMessage:
	text: str | None = None
	object: FocusedObject | None = None

	def to_dict(self) -> dict :
		return {
			"text" : self.text,
			"object" : self.object.to_dict() if self.object else None
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "BotMessage":
		return cls(
			text=data.get('text'),
			object=FocusedObject.from_dict(data["object"]) if data.get('object') else None
		)

@dataclass(slots=True)
class ProcessResult(BaseModel):
	sender_id: str
	message_id: str
	messages: list[BotMessage]