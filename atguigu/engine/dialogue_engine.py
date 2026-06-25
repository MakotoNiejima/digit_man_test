import time
from typing import List

from atguigu.clarify.responder import ClarifyReason
from atguigu.domain.messages import UserMessage, ProcessResult, BotMessage, MessageType
from atguigu.domain.state import DialogueState, FocusedObject
from atguigu.plan.planner import TurnPlanner
from atguigu.task.command.commands import Command, SetSlotsCommand
from atguigu.task.flow.flows import FlowsList
from atguigu.task.flow.steps import CollectFlowStep
from atguigu.task.handler import TaskHandler


class DialogueEngine :

	def __init__(
			self,
			turn_planner: TurnPlanner,  # 任务路由器
			task_handler: TaskHandler,  # 业务任务处理器
			knowledge_handler: KnowledgeHandler,  #
	) :

		self.clarify_responder = None
		self.turn_plan_validator = None
		self.turn_planner = turn_planner
		self.task_handler = task_handler
		self.knowledge_handler = knowledge_handler

	async def process_message(self, state: DialogueState,
	                          user_message: UserMessage) -> ProcessResult :
		"""处理一条消息，直接修改state，返回本轮结果"""
		# 1.准备会话（超时检查/新建）
		self._prepare_session(state)
		# 2.开启本轮turn（写入pending_turn）
		self._begin_turn(state, user_message)

		# 3.按消息类型进行分类
		user_message_type = user_message.type
		if user_message_type == MessageType.TEXT :
			messages = await self._handle_text_message(
				user_message,
				state=state,
				flow_list=self.task_handler.flow_list,
				knowledge_intents=self.knowledge_handler.konwledge_intents)
		else :
			# 将state里面的focused_object赋值
			state.set_focused_object(user_message.object)
			messages = await self._handle_object_message(message=user_message, state=state)

		# 4.不论什么回复都写进turn，并提交
		state.pending_turn.bot_massages.extend(messages)
		state.commit_pending_turn()

		# 5。组装返回结果
		return ProcessResult(
			sender_id=user_message.sender_id,
			message_id=user_message.message_id,
			messages=messages
		)

	def _prepare_session(self, state: DialogueState) -> None :
		# 仅做开启引擎用
		current_session = state.current_session()
		now = time.time()
		if current_session is None :
			state.start_session()
			return
		if now - current_session.last_activity_time > 60 * 60 :
			state.close_session()
			state.reset_running_state_for_new_session()
			state.start_session()
			return
		else :
			current_session.last_activity_time = now

	async def _handle_text_message(self, user_message,state,flow_list,knowledge_intents) -> List[BotMessage] :
		# 如果是文本消息，调用大模型进行意图识别，返回command对象
		# 1.调用大语言模型，生成本轮计划
		turn_plan = await self.turn_planner.predict(
			user_message=user_message,
			state=state,
			flow_list=flow_list,
			knowledge_intents=knowledge_intents
		)
		# 2.validate防幻觉校验
		validation = self.turn_plan_validator.validate(
			turn_plan,
			state=state,
			knowledge_intents=self.knowledge_handler.konwledge_intents
		)
		if not validation.valid :
			# 如果校验失败，走意图澄清
			return await self.clarify_responder.respond(state=state, reason=validation.reason)
		# 3.按轨道分发,三个轨道进行
		if turn_plan.task is not None :
			# 返回业务结果
			return await self.task_handler.handle(
				commands=turn_plan.task.commands,
				state=state,
			)
		elif turn_plan.knowledge is not None :
			if state.active_task :
				state.interrupt_activating_task()
			# 返回知识查询节点处理结果
			return await self.knowledge_handler.handle(
				state=state,
				intents=turn_plan.knowledge.intents,
			)
		# 闲聊兜底
		if state.active_task :
			state.interrupt_activating_task()
		return await self.knowledge_handler.handle(state=state)

	async def _handle_object_message(self,
	                                 message: UserMessage,
	                                 state: DialogueState, ) -> List[BotMessage] :
		commands = self._resolve_object_commands(
			message=message,
			state=state,
			flows=self.task_handler.flows,
		)
		if commands :
			# 场景A：对象能填当前槽位，直接推荐流程
			return await self.task_handler.handle(commands=commands, state=state)
		# 未匹配到slot，不打断，让流程继续
		if state.active_task is not None :
			return await self.knowledge_handler.handle(commands=[], state=state)

		return await self.clarify_responder.respond(state=state, reason=ClarifyReason.OBJECT_REQUIRES_INTENT)

	def _begin_turn(self, state, user_message) :
		state.begin_turn(user_message)

	def _resolve_object_commands(self,
	                             message: UserMessage,
	                             state: DialogueState,
	                             flows: FlowsList
	                             ) -> list[Command] :
		message_object = message.object
		if message_object is not None :
			return []

		object_type = message_object.type.strip().lower()

		if object_type == "order" :
			if self._try_build_slots_command(state, flows, "order_number") :
				return [
					SetSlotsCommand(
						command="set_slots",
						slots={"product_id" : message_object.id}
					)
				]
			return []
		if object_type == "product" :
			if self._try_build_slots_command(state, flows, "product_id") :
				return [
					SetSlotsCommand(
						command="set_slots",
						slots={"product_id" : message_object.id}
					)
				]
			return []
		return []

	@staticmethod
	def _try_build_slots_command(
			state: DialogueState,
			flows: FlowsList,
			slot_name: str
	) -> bool :
		# 回答一个问题，当前流程是不是为了定义某个收集槽，而且这个槽位还没填
		active_task = state.active_task
		if active_task is not None :
			return False
		flow = flows.get_flow_by_id(active_task.flow_id)
		if flow is None:
			return False
		if active_task.slots.get(slot_name) :
			return False
		for step in flow.steps :
			if isinstance(step, CollectFlowStep) and step.slot_name == slot_name :
				return True

		return False
