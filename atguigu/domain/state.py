"""
对话状态聚合根
"""
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.contexts import TaskContext, SystemContext
from atguigu.domain.messages import BotMessage, UserMessage

@dataclass(slots=True)
class FocusedObject :
	type: str
	id: str
	title: str | None = None
	attributes: dict = field(default_factory=dict)

	def to_dict(self) -> dict[str, Any] :
		return {
			'type' : self.type,
			'id' : self.id,
			'title' : self.title,
			'attributes' : self.attributes
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> 'FocusedObject' :
		return cls(
			type=data['type'],
			id=data['id'],
			title=data['title'],
			attributes=data['attributes']
		)

@dataclass(slots=True)
class Turn :
	turn_id: str  # uuid
	user_message: UserMessage
	bot_massages: list[BotMessage] | None = None

	def to_dict(self) -> dict[str, Any] :
		return {
			'turn_id' : self.turn_id,
			'user_message' : self.user_message,
			'bot_massages' : [bot_massage for bot_massage in self.bot_massages],
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> 'Turn' :
		return cls(
			turn_id=data['turn_id'],
			user_message=UserMessage.from_dict(data['user_message']),
			bot_massages=[BotMessage.from_dict(bot_massage_dict) for bot_massage_dict in data.get("bot_massages")]
		)

@dataclass(slots=True)
class Session :
	session_id: str
	started_at: float
	last_activity_time: float  # 用于判断超时的时间戳
	closed_at: float | None = None
	turns: list[Turn] = field(default_factory=list)

	def to_dict(self) -> dict[str, Any] :
		return {
			'session_id' : self.session_id,
			'started_at' : self.started_at,
			'last_activity_time' : self.last_activity_time,
			'closed_at' : self.closed_at,
			'turns' : [turn.to_dict() for turn in self.turns]
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> 'Session' :
		return cls(
			session_id=data['session_id'],
			started_at=data['started_at'],
			last_activity_time=data['last_activity_time'],
			closed_at=data['closed_at'],
			turns=[Turn.from_dict(turn_dict) for turn_dict in data.get('turns', [])]
		)

@dataclass
class DialogueState :
	"""
	聚合根
	"""
	sender_id: str  # 用户唯一标识
	active_task: TaskContext | None = None
	paused_tasks: list[TaskContext] = field(default_factory=list)
	active_system_task: SystemContext | None = None
	focused_object: FocusedObject | None = None
	sessions: list[Session] = field(default_factory=list)
	current_session_id: str | None = None
	pending_turn: Turn | None = None

	def to_dict(self) -> dict :
		return {
			'sender_id' : self.sender_id,
			'active_task' : self.active_task.to_dict() if self.active_task else None,
			'paused_task' : [paused_task.to_dict() for paused_task in self.paused_tasks],
			'active_system_task' : self.active_system_task.to_dict() if self.active_system_task else None,
			'focused_object' : self.focused_object.to_dict() if self.focused_object else None,
			'sessions' : [session.to_dict() for session in self.sessions],
			'current_session_id' : self.current_session_id,
			'pending_turn' : self.pending_turn.to_dict() if self.pending_turn else None,
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> 'DialogueState' :
		return cls(
			sender_id=data['sender_id'],
			active_task=TaskContext.from_dict(data.get('active_task')),
			paused_tasks=[TaskContext.from_dict(tasks) for tasks in data.get('paused_tasks', [])],
			active_system_task=SystemContext.from_dict(data.get('active_system_task')),
			focused_object=FocusedObject.from_dict(data.get('focused_object')),
			sessions=[Session.from_dict(session) for session in data.get('sessions', [])],
			current_session_id=data.get('current_session_id'),
			pending_turn=Turn.from_dict(data['pending_turn']) if data.get('pending_turn') else None,
		)

	# ++++++++++++++++++++组合方法++++++++++++++++++++++++++++++++
	# --------------------任务相关--------------------------------
	def start_active_system_task(self, system_context: SystemContext) :
		# 当TurnPlanner判断用户发起来一个新业务任务时，把传进来的TaskContext设置为活跃任务
		self.active_system_task = system_context

	def end_activating_system_task(self) :
		"""
		 结束正在激活的系统流程(任务)
		:return:
		"""
		self.active_system_task = None

	def start_active_business_task(self, task_context: TaskContext) -> None :
		"""
		开启并激活业务流程(任务)
		:param task_context:
		:return:
		"""
		self.active_task = task_context

	def end_activating_business_task(self) -> None :
		"""
		 结束正在激活的业务流程(任务))
		:return:
		"""
		self.active_task = None

	def end_activating_task(self) :
		self.active_system_task = None
		self.active_task = None

	def interrupt_activating_task(self) :
		"""只负责中断，也就是开启下一个任务时用，故系统流程会跳到中断"""
		self.paused_tasks.append(self.active_task)
		self.active_task = None

	def resume_task(self, flow_id: str | None = None)-> bool :
		if not self.paused_tasks :
			return False

		if flow_id is None :
			paused_task = self.paused_tasks.pop()
			self.active_task = paused_task
			return True

		for i,task in enumerate(self.paused_tasks) :
			if task.flow_id == flow_id :
				self.active_task = task
				del self.paused_tasks[i]
				return True
			else :
				task = self.paused_tasks.pop()
				self.active_task = task
				return True
		return False

	def current_activating_task(self) :
		return self.active_system_task or self.active_task

	# --------------------槽位相关--------------------------------
	def set_slots(self,slots: dict[str, Any]):
		"""
		设置槽位
		:param slots:
		:return:
		"""
		if self.active_task is not None :
			self.active_task.slots.update(slots)

	def get_slots(self,slot_name) -> dict[str, Any] :
		return self.active_task.slots.get(slot_name)

	# --------------------卡片相关--------------------------------
	def set_focused_object(self,focused_object: FocusedObject) :
		self.focused_object = focused_object
	# --------------------session相关----------------------------

	def current_session(self)-> Session | None:
		for session in self.sessions :
			if session.session_id == self.current_session_id :
				return session
		return None

	def start_session(self):
		now = time.time()
		session = Session(session_id=str(uuid.uuid4()), started_at=now, last_activity_time=now)
		self.current_session_id = session.session_id
		self.sessions.append(session)

	def close_session(self):
		if self.current_session() is not None :
			self.current_session().closed_at = time.time()
			self.current_session_id = None

	def reset_running_state_for_new_session(self):
		self.active_task = None
		self.paused_tasks = list()
		self.active_system_task = None
		
		self.focused_object = None

	# --------------------Turn(轮次)相关----------------------------
	def start_turn(self,user_message: UserMessage):
		if self.current_session() is not None :
			turn = Turn(turn_id=str(uuid.uuid4()),user_message=user_message,bot_massages=[])

	def commit_pending_turn(self) :
		"""
		提交缓冲区的内容
		:return:
		"""
		self.current_session().turns.append(self.pending_turn)
		self.pending_turn = None




















