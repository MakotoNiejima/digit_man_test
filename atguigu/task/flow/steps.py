from dataclasses import dataclass, field
from typing import Any
from enum import Enum

from atguigu.task.flow.links import FlowStepLink, FlowStepStaticLink, FlowStepFallbackLink, FlowStepConditionLink

#+++++++++++++一句回复怎么生成的数据模板+++++++++++++
@dataclass(slots=True)
class ResponseDefinition:
	text: str | None = None
	mode: str = "static"
	prompt: str = None

@dataclass(slots=True)
class SoltValidation:
	condition: str | None = None
	failure_response: ResponseDefinition | None = None

#step的类型，Enum枚举做校验，不用到处写字符串
class FlowStepType(Enum) :
	START = 'start'
	COLLECT = 'collect'
	ACTION = 'action'
	END = 'end'


@dataclass(slots=True)
class FlowStep :
	"""
	步骤基类，四种类型通用字段
	"""
	id: str  #步骤ID
	type: FlowStepType
	next: list[FlowStepLink] = field(default_factory=list)

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
		step_type = data["type"]
		clz = FLOW_STEP_TYPE_CLASS[step_type]  #得到子类
		return clz.from_dict(data)

	@staticmethod
	def _load_base_fields(step_data: dict[str, Any]) -> dict[str, Any]:
		return {
			'id': step_data["id"],
			'type': FlowStepType(step_data["type"]),
			'next': FlowStep.build_links(step_data["next"]),
		}

	#links内不做转换，只负责定义数据类型！解析逻辑放在steps里
	@classmethod
	def build_links(cls,link: str | list[dict[str,Any]]) -> list[FlowStepLink]:
		links: list[FlowStepLink] = []
		if isinstance(link, str) :
			links.append(FlowStepStaticLink(target=link))
		else:
			for condition_link in link :
				if "if" in condition_link :
					links.append(FlowStepConditionLink(condition=condition_link["if"]))
				else:
					links.append(FlowStepFallbackLink(target=condition_link["else"]))
		return links

#四个子步骤类
@dataclass(slots=True)
class StartFlowStep(FlowStep) :
	@classmethod
	def from_dict(cls, data: dict[str, Any]):
		return cls(**FlowStep._load_base_fields(data))

@dataclass(slots=True)
class ActionFlowStep(FlowStep) :
	"""
	定义属于自己步骤类型的字段
	"""
	action: str = ""  #response , listen , action_xxx
	args: dict[str,Any] = field(default_factory=dict)  #需要给外部的数据都放在这里，包括给前端的数据，需要第三方返回东西的参数等

	@classmethod
	def from_dict(cls, step_data: dict[str, Any])-> "ActionFlowStep":
		return cls(
			**FlowStep._load_base_fields(step_data),
			action=step_data["action"],
			args=step_data.get("args")
		)

@dataclass(slots=True)
class CollectFlowStep(FlowStep) :
	slot_name: str = ""
	response: ResponseDefinition = field(default_factory=ResponseDefinition)
	validate: SoltValidation | None = None

	@classmethod
	def from_dict(cls, step_data: dict[str, Any])-> "CollectFlowStep":
		return cls(
			**FlowStep._load_base_fields(step_data),
			slot_name=step_data.get("slot_name"),
			response=ResponseDefinition(
				text=step_data["response"].get("text"),
				mode=step_data["response"].get("mode"),
				prompt=step_data["response"].get("prompt")
			),
			validate=SoltValidation(
				condition=step_data["validate"]["condition"],
				failure_response=ResponseDefinition(
					text=step_data["validate"]["failure_response"]["text"],
					mode=step_data["validate"].get("failure_response").get("mode"),
					prompt=step_data["validate"]['failure_response'].get("prompt")
				)if step_data["validate"].get("failure_response") else None
			)if step_data.get('validate') else None
		)

@dataclass(slots=True)
class EndFlowStep(FlowStep) :
	@classmethod
	def from_dict(cls, step_data: dict[str, Any])-> "EndFlowStep":
		return cls(
			**FlowStep._load_base_fields(step_data),
		)
	pass

FLOW_STEP_TYPE_CLASS:dict[str, type[FlowStep]] = {
	'start': StartFlowStep,
	'collect': CollectFlowStep,
	'action': ActionFlowStep,
	'end': EndFlowStep,
}

