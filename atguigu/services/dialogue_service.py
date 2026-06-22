from atguigu.domain.messages import UserMessage, ProcessResult
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository


class DialogueService:
	def __init__(self,dialogue_repository:DialogueRepository,dialogue_engine:DialogueEngine):
		self.dialogue_repository = dialogue_repository
		self.dialogue_engine = dialogue_engine

	async def hand_dialogue(self,user_message:UserMessage)->ProcessResult:
		state = await self.dialogue_repository.load_dialogue(user_message.sender_id)
		process_result = await self.dialogue_engine.process_message(state,user_message)
		await self.dialogue_repository.save_dialogue(state)
		return process_result