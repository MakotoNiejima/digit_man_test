from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.command.commands import Command
from atguigu.task.flow.flows import FlowsList


class TaskHandler:
	def __init__(self,
	             command_process:CommandProcessor,
	             flow_list:FlowsList,
	             flow_executor:FlowExecutor,
	             action_runner:ActionRunner
	             ):
	async def handle(self,commands:list[Command],state:DialogueState)->list[BotMessage]:
		self.command_processor.run(commands,state,self.flows)
		messages: list[BotMessage] = await self.flow_executor.run_task(state, self.flows, self.action_runner)
		return messages