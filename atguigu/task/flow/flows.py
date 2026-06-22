from dataclasses import dataclass, field
from typing import List

from atguigu.task.flow.steps import FlowStep


@dataclass(slots=True)
class FlowSlot:
	name: str
	type: str
	description: str
	label: str

@dataclass(slots=True)
class Flow:
	flow_id: str
	flow_name: str
	description: str
	steps: List[FlowStep] = field(default_factory=list)
	slots: dict[str, FlowSlot] = field(default_factory=dict)

class UserFlow:
	pass

class SystemFlow:
	pass
@dataclass(slots=True)
class FlowsList:
	flows: List[Flow] = field(default_factory=list)
	slots: dict[str, FlowSlot] = field(default_factory=dict)
	pass
