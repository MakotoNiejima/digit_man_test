import json
from dataclasses import asdict
from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import load_prompt, PromptTemplate

from atguigu.domain.messages import UserMessage
from atguigu.domain.state import DialogueState
from atguigu.history.builder import ChatHistoryBuilder
from atguigu.infrastructure.llm_client import llm_client
from atguigu.knowledge.knowledge_intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan
from atguigu.task.flow.flows import FlowsList, Flow


class TurnPlanner :
	# 操作大模型
	async def predict(self,
	                  user_message: UserMessage,
	                  *
	                  state: DialogueState,
	                  flow_list: FlowsList,  # 系统支持的所有流程
	                  knowledge_intents: dict[str, KnowledgeIntent]  # 系统支持的所有意图
	                  ) -> TurnPlan :
		prompt_inputs = self._build_prompt_inputs(user_message,state=state, flow_list=flow_list, knowledge_intents=knowledge_intents)
		return await self._predict_from_prompt_inputs(prompt_inputs)

	def _build_prompt_inputs(self,user_message, state, flow_list, knowledge_intents) -> dict[str, Any] :
		user_massage = ChatHistoryBuilder.process_user_message(user_message)
		current_conversation = ChatHistoryBuilder.build(state.current_session().turns[-10 :])
		active_task = json.dumps(state.active_task.to_dict(), ensure_ascii=False) if state.active_task else None
		focused_object_json = json.dumps(state.focused_object.to_dict(),
		                                 ensure_ascii=False) if state.focused_object else None
		interrupted_tasks_json = json.dumps(state.interrupted_tasks,
		                                    ensure_ascii=False
		                                    ) if state.interrupted_tasks else None
		available_flows_json = json.dumps({
			"flows" :[
				{k : v for k, v in asdict(flow).items() if k != "steps"
			} for flow in flow_list.flows if not flow.flow_id.startswith("system_")
			]
		},ensure_ascii=False)
		knowledge_intents = json.dumps(
			[{"id": intent.id,"description":intent.description
			  }for intent in knowledge_intents.values()], ensure_ascii=False) if knowledge_intents else None
		return {
			"user_message" : user_massage,  # 用户说了什么
			"current_conversation" : current_conversation,  # 当前上下文，最多十轮
			"available_flows_json" :available_flows_json,
			# 可用flow列表
			"active_task_json" : active_task,  # 正在进行的业务
			"interrupted_tasks_json" : interrupted_tasks_json,  # 被中断的业务列表
			"focused_object_json" : focused_object_json,  # 卡片对象
			"knowledge_intents_json" : knowledge_intents,  # 可用意图列表
		}

	async def _predict_from_prompt_inputs(self, prompt_inputs) -> TurnPlan :
		prompt_text = load_prompt("turn_plan")
		prompt = PromptTemplate.from_template(prompt_text, template_format="jinja2")

		chain = prompt | llm_client | JsonOutputParser()
		result = await chain.ainvoke(
			prompt_inputs,
		)
		return TurnPlan.from_dict(result)
