from dataclasses import dataclass
from typing import Any


@dataclass
class Command:
	command: str

	@classmethod
	def from_json(cls, data: dict[str, Any])->"Command":
		clz = COMMAND_NAME_TO_CLASS[data["command"]]
		return clz(**data)

@dataclass
class StartFlowCommand(Command):
	flow: str

@dataclass
class SetSlotsCommand(Command):
	slot: dict[str, Any]

@dataclass
class CancelFlowCommand(Command):
	pass

@dataclass
class ResumeFlowCommand(Command):
	flow: str

COMMAND_NAME_TO_CLASS = {
	"start": StartFlowCommand,
	"set_slots": SetSlotsCommand,
	"cancel": CancelFlowCommand,
	"resume": ResumeFlowCommand
}