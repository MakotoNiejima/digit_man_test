import json

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState
from atguigu.model.dialogue_state import DialogueStateRecord


class DialogueRepository:
	"""
	对话的持久层组件（读写数据库customer——severice）
	"""
	def __init__(self,session:AsyncSession):
		self.session = session

	async def load_dialogue(self,sender_id: str)->DialogueState:

		stmt = select(DialogueStateRecord).where(DialogueStateRecord.sender_id == sender_id)
		cursor = await self.session.execute(stmt)
		result = cursor.scalar_one_or_none()
		if result:
			return DialogueState.from_dict(json.loads(result.state_json))
		return DialogueState(sender_id=sender_id)

	async def save_dialogue(self,dialogue_state:DialogueState):
		dialogue_str = json.dumps(dialogue_state.to_dict(),ensure_ascii=False)

		# 2. 定义SQL
		insert_stmt = insert(DialogueStateRecord).values(
			sender_id=dialogue_state.sender_id, state_json=dialogue_str
		)

		# SQL语句升级：insert 语句升级到update 语句  条件重复的key[主键]
		upsert_stmt = insert_stmt.on_duplicate_key_update(
			state_json=insert_stmt.inserted.state_json
		)

		# INSERT INTO
		# dialogue_state_record(sender_id, state_json)
		# VALUES(: sender_id, :state_json)
		# ON DUPLICATE KEY UPDATE
		# state_json = VALUES(state_json);
		# 3. 执行SQL
		await self.session.execute(upsert_stmt)

		# 4. commit
		await self.session.commit()

