from dataclasses import dataclass, field
from typing import Any

from atguigu.task.command.commands import Command


@dataclass
class ChitChatTurnPlan :
	pass

@dataclass
class KnowLedgeTurnPlan :
	intents:list[str] = field(default_factory=list)

	@classmethod
	def from_dict(cls,knowledge: dict) -> "KnowLedgeTurnPlan":
		return cls(intents=knowledge["intents"])

@dataclass
class TaskTurnPlan :
	#llm可能会返回多个command，用于指示下一步怎么走
	commands: list[Command] = field(default_factory=list)

	@classmethod
	def from_dict(cls,task: dict[str,Any]) -> "TaskTurnPlan":
		return cls(commands=[Command.from_dict(command) for command in task["commands"]])

@dataclass
class TurnPlan:
	task: TaskTurnPlan | None = None
	knowledge:KnowLedgeTurnPlan | None =None
	chitchat:ChitChatTurnPlan | None = None

	@classmethod
	def from_dict(cls,data: dict) -> "TurnPlan":
		return cls(
			task=TaskTurnPlan.from_dict(data["task"]) if data.get("task") else None,
			knowledge=KnowLedgeTurnPlan.from_dict(data["knowledge"]) if data.get("knowledge") else None,
			chitchat=ChitChatTurnPlan() if data.get("chitchat") else None,
		)