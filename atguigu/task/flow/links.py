from dataclasses import dataclass


@dataclass(slots=True)
class FlowStepLink:
	"""
	基类使用，只提供目标，也就是下一个步骤的id
	"""
	target : str

@dataclass(slots=True)
class FlowStepStaticLink(FlowStepLink):
	pass

@dataclass(slots=True)
class FlowStepConditionLink(FlowStepLink):
	condition: str  #条件字符串，eval()计算

@dataclass(slots=True)
class FlowStepFallbackLink(FlowStepLink):
	pass
