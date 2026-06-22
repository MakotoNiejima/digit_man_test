from dataclasses import dataclass
from typing import Any


@dataclass
class Command:
	command: str

	@classmethod
	def from_json(cls, data: dict[str, Any])->"Command":
		clz = COMMAND_NAME_TO_CLASS[data["command"]]
		return clz(**data)




COMMAND_NAME_TO_CLASS = {}