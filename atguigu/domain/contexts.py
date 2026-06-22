"""
上下文：动态的东西，变化的东西，装进去承载动态可变的内容
定义两个数据模型，分别服务于：业务流程 与 系统流程
"""
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class TaskContext :
	"""
	业务流程的上下文（某一运行期间的一个业务流程信息）
	"""
	flow_id: str
	step_id: str | None = None  # 在刚进入对话时，可以是没有步骤的
	slots: dict[str, Any] = field(default_factory=dict)  # 槽位,必须用field 配和默认工厂来配置{}空字典，不然可能存在内存共用

	# 序列化方法，即转换成可传输与存储的序列化结果，这样后续才能传进数据库,实例 > 字典》 JSON 》写库
	def to_dict(self) -> dict[str, Any] :
		return {
			"flow_id" : self.flow_id,
			"step_id" : self.step_id,
			"slots" : dict(self.slots),
		}

	# 读库》JSON 》 字典 》 实例
	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "TaskContext" :
		return cls(
			flow_id=data["floww_id"],
			step_id=data["step_id"],
			slots=data["slots"]
		)


@dataclass(slots=True)
class SystemContext :
	system_flow_id: str  # 实际上是一个英文名称
	system_step_id: str | None = None

	def to_dict(self) -> dict[str, Any] :
		return asdict(self)

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "SystemContext" :
		clz = FLOW_ID_TO_CONTEXT_CLASS[data["flow_id"]]
		return clz(**data)


@dataclass(slots=True)
class StartedSystemContext(SystemContext) :
	started_flow_id: str = ""  # 新开始的业务流程
	started_flow_name: str = ""  # 新开始的业务流程显示名，中文


@dataclass(slots=True)
class InterruptedSystemContext(SystemContext) :
	# 被打断的用户流id
	interrupted_flow_id: str = ""
	# 被打断的用户流别名
	interrupted_flow_name: str = ""
	# 新启动的流id
	started_flow_id: str = ""
	# 新启动的流别名
	started_flow_name: str = ""


@dataclass(slots=True)
class CanceledSystemContext(SystemContext) :
	# 被取消的业务流id
	canceled_flow_id: str = ""
	# 被取消的业务流名称
	canceled_flow_name: str = ""

@dataclass(slots=True)
class ResumedSystemContext(SystemContext) :
	resumed_flow_id: str = ""
	resumed_flow_name: str = ""


@dataclass(slots=True)
class CollectedSystemContext(SystemContext) :
	"""
	填槽位用
	在业务流程主动声明：我需要这个槽位时，触发，用来收集用户返回的信息
	作用是把我需要XXX数据说出来
	"""

	slot_name: str = ""
	#回复给用户的消息，比如告诉我你的订单号
	response: dict[str, Any] = field(default_factory=dict)


# 数据库返回的只是flow_id,通过这个flow_id,查到反序列化的子类对象
FLOW_ID_TO_CONTEXT_CLASS = {
	"system_task_started" : StartedSystemContext,
	"system_task_interrupted" : InterruptedSystemContext,
	"system_task_canceled" : CanceledSystemContext,
	"system_task_resumed" : ResumedSystemContext,
	"system_collect_information" : CollectedSystemContext
}

if __name__ == '__main__' :
	active_task = TaskContext(flow_id="退款业务", step_id="正在处理退款", slots={})
	active_system_task = StartedSystemContext(
		system_flow_id="system_task_started",
		system_step_id="ackonwledge",
		started_flow_id="退款业务",
		started_step_name="退款申请"
	)
