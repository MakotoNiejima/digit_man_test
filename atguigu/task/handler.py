from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.command.commands import Command, StartFlowCommand
from atguigu.task.flow.flows import FlowsList


class TaskHandler:
	def __init__(self,
	             command_process:CommandProcessor,
	             flow_list:FlowsList,
	             flow_executor:FlowExecutor,
	             action_runner:ActionRunner
	             ):
		self.command_processor = command_process
		self.flow_list = flow_list
		self.flow_executor = flow_executor
		self.action_runner = action_runner

	async def handle(self,
					 commands:list[Command],
					 state:DialogueState
					 )->list[BotMessage]:

		self.command_processor.run(commands,state,self.flow_list)
		#先让CommandProcessor改状态，再让FlowExecutor推进流程
		messages: list[BotMessage] = await self.flow_executor.run_task(
			state, self.flow_list, self.action_runner)

		return messages





