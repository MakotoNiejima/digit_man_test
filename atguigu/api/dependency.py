from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from atguigu.infrastructure import database  # 没问题  相当于把整个模块导入过来
#如果这里直接导session——factory，导入的是默认值none，涉及到python的导包问题，如果session——factory有初始值，
# 并且后续会被修改，则直接导包导的会是默认值，因为导包是最优先处理的，直接导模块则可以解决此事
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository
from atguigu.services.dialogue_service import DialogueService

dialogue_engine : DialogueEngine | None =None


def init_dialogue_engine():
	global dialogue_engine

def get_engine():
	return dialogue_engine

DialogueEngineDep = Annotated[DialogueEngine, Depends(get_engine)]

async def get_session():
	async with database.session_factory() as session:
		yield session

RepositorySessionDep = Annotated[AsyncSession, Depends(get_session)]

async def get_repository(session: RepositorySessionDep):
	return DialogueRepository(session=session)

DialogueRepositoryDep = Annotated[DialogueRepository, Depends(get_repository)]

def get_dialogue_service(
		engine: DialogueEngineDep,
		repo: DialogueRepositoryDep
	):

	return DialogueService(
		dialogue_engine=engine,
		dialogue_repository=repo
	)
# Annotated:将类型以及类型的元素
DialogueServiceDep = Annotated[DialogueService, Depends(get_dialogue_service)]
