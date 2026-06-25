from dataclasses import dataclass, field
from typing import List

from atguigu.task.flow.steps import FlowStep, StartFlowStep


@dataclass(slots=True)
class FlowSlot:
	name: str
	type: str
	description: str
	label: str

@dataclass(slots=True)
class Flow:
	#把两个流放在了一起
	flow_id: str
	flow_name: str
	description: str
	steps: List[FlowStep] = field(default_factory=list)
	slots: dict[str, FlowSlot] = field(default_factory=dict)

	def get_start_step(self)-> StartFlowStep | None:
		for step in self.steps:
			if isinstance(step,StartFlowStep):
				return step
		return None

class UserFlow:
	pass

class SystemFlow:
	pass
@dataclass(slots=True)
class FlowsList:
	flows: List[Flow] = field(default_factory=list)
	slots: dict[str, FlowSlot] = field(default_factory=dict)

	def get_flow_by_id(self,flow_id: str) -> Flow | None:
		for flow in self.flows:
			if flow.flow_id==flow_id:
				return flow
		return None