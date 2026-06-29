
from atguigu.domain.messages import UserMessage, ProcessResult, ChatHistoryMessage
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository
from atguigu.history.builder import ChatHistoryBuilder


class DialogueService :
	def __init__(self, dialogue_repository: DialogueRepository, dialogue_engine: DialogueEngine) :
		self.dialogue_repository = dialogue_repository
		self.dialogue_engine = dialogue_engine

	async def hand_dialogue(self, user_message: UserMessage) -> ProcessResult :
		state = await self.dialogue_repository.load_dialogue(user_message.sender_id)
		process_result = await self.dialogue_engine.process_message(state, user_message)
		await self.dialogue_repository.save_dialogue(state)
		return process_result

	async def load_chat_history(self, sender_id: str) -> list[ChatHistoryMessage] :
		"""通过用户的id，去数据库找聚合根，组装成历史回复列表，以每条对话为单位"""
		# 1.先通过id找聚合根，直接返回state
		dialogue_state = await self.dialogue_repository.load_dialogue(sender_id)
		# 2.从sessions列表中取出session
		sessions = dialogue_state.sessions
		chat_history = []
		for session in sessions :
			for turn in session.turns :
				ChatHistoryBuilder.built_chat_history(
					session_id=session.session_id,
					role="bot",
					text=turn.user_message.text,
					obj=turn.user_message.object
				)
				if turn.bot_massages is not None :
					for bot_message in turn.bot_massages :
						ChatHistoryBuilder.built_chat_history(
							session_id=session.session_id,
							role="bot",
							text=bot_message.text,
							obj=bot_message.object
						)

		return chat_history
