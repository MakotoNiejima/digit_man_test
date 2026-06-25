from atguigu.clarify.responder import TurnPlanValidationResult, ClarifyReason
from atguigu.domain.state import DialogueState
from atguigu.knowledge.knowledge_intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan
from atguigu.task.command.commands import StartFlowCommand, ResumeFlowCommand, CancelFlowCommand, SetSlotsCommand
from atguigu.task.flow.flows import FlowsList


class TurnPlanValidator :
	def validate(self,
	             turn_plan: TurnPlan,
	             state: DialogueState,
	             knowledge_intents: dict[str, KnowledgeIntent],
	             flows: FlowsList,
	             ) -> TurnPlanValidationResult :
		active_tracks = self._active_track(turn_plan)

		if not active_tracks :
			return self._reject(ClarifyReason.MISSING_TRACK)
		if len(active_tracks) > 1 :
			return self._reject(ClarifyReason.MULTIPLE_TASK_FLOWS)
		track = active_tracks[0]
		if track == "task" :
			return self._validate_task(turn_plan, flows=flows)
		if track == "knowledge" :
			return self._validate_knowledge(turn_plan, state=state, knowledge_intents = knowledge_intents)

		return TurnPlanValidationResult(valid=True)

	@staticmethod
	def _active_track(self, turn_plan) -> list[str] :
		"""数一下命中几个轨道"""
		tracks: list[str] = []
		if turn_plan.task is not None :
			tracks.append('task')
		if turn_plan.knowledge is not None :
			tracks.append('knowledge')
		if turn_plan.chitchat is not None :
			tracks.append('chitchat')
		return tracks

	def _reject(self, reason:ClarifyReason) -> TurnPlanValidationResult :
		return TurnPlanValidationResult(valid=False,reason=reason)

	def _validate_task(self,
	                   turn_plan: TurnPlan,
	                   flows: FlowsList,
	                   ) -> TurnPlanValidationResult :
		task_plan = turn_plan.task

		#第一重：commands不能为空
		if task_plan is None or task_plan.commands is None :
			return self._reject(ClarifyReason.MISSING_TASK_COMMANDS)

		#第二重，commands必须认识
		allowed = (StartFlowCommand,CancelFlowCommand, SetSlotsCommand,ResumeFlowCommand,)
		if not all(isinstance(cmd,allowed) for cmd in task_plan.commands) :
			return self._reject(ClarifyReason.MISSING_TASK_COMMANDS)

		#第三重：不能一次开多个流程
		start_commands = [cmd for cmd in task_plan.commands if isinstance(cmd,StartFlowCommand)]
		if len(start_commands) > 1 :
			return self._reject(ClarifyReason.MULTIPLE_TASK_FLOWS)

		#第四重：要开的流程必须真实存在
		if start_commands:
			flow = flows.get_flow_by_id(start_commands[0].flow)
			if flow is None :
				return self._reject(ClarifyReason.UNKNOWN_TASK_FLOW)
		return TurnPlanValidationResult(valid=True)

	def _validate_knowledge(self, turn_plan, state,knowledge_intents:dict[str,KnowledgeIntent]) -> TurnPlanValidationResult    :
		knowledge_plan = turn_plan.knowledge

		if knowledge_plan is None or knowledge_plan.intents is not None :
			return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)

		focused_object = state.focused_object
		for intent in knowledge_plan.intents :
			intent_meta = knowledge_intents[intent]
			required_object = intent_meta.requires_object
			if required_object is not None :
				if required_object is not None or focused_object.type != required_object :
					return self._reject(ClarifyReason.MISSING_FOCUSED_OBJECT)
		return TurnPlanValidationResult(valid=True)











