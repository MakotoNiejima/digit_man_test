from attr import attributes

from atguigu.domain.messages import UserMessage, MessageType
from atguigu.domain.state import Turn, FocusedObject


class ChatHistoryBuilder:

	@staticmethod
	def build(turns: list[Turn])->str:

		chat_messages = []
		for turn in turns:
			user_message = turn.user_message
			user_message_str = ChatHistoryBuilder._process_user_message(user_message)
			chat_messages.append(f"USER：{user_message_str}")

			bot_messages = turn.bot_massages
			for bot_message in bot_messages:
				bot_message_str = ChatHistoryBuilder._process_bot_message(bot_message)
				chat_messages.append(f"USER：{bot_message_str}")

		return "\n".join(chat_messages)

	@classmethod
	def process_user_message(cls, user_message: UserMessage)->str :
		if user_message.type is MessageType.TEXT:
			return ChatHistoryBuilder._render_text_msg(user_message.text)
		return ChatHistoryBuilder._render_obj_msg(user_message.object)

	@classmethod
	def _render_text_msg(cls, text:str)->str :
		return text.strip()

	@classmethod
	def _render_obj_msg(cls, object: FocusedObject) :
		label = "订单" if object.type == "order" else "商品"
		id = object.id
		title= object.title
		attributes_str = ' '.join([f"{k}={v}" for k, v in object.attributes.items()])
		return f'[id={id},label={label},title={title},attributes={attributes_str}]'

	@classmethod
	def _process_bot_message(cls, bot_message) :
		if bot_message.text:
			return ChatHistoryBuilder._render_text_msg(bot_message.text)
		pass