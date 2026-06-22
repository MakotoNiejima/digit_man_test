from contextlib import asynccontextmanager

from fastapi import FastAPI

from atguigu.api.dependency import init_dialogue_engine
from atguigu.api.router.chat_router import router
from atguigu.infrastructure.database import init_db_engine, dispose_engine
from atguigu.infrastructure.http_client import init_http_client, dispose_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""
	启动服务器的时候会来调用，在处理路由之前把初始化的东西做完
	:param app:
	:return:
	"""
	await init_db_engine()
	init_http_client()
	init_dialogue_engine()

	await dispose_engine()
	await dispose_http_client()

app = FastAPI(description="智能客服1.0",lifespan=lifespan)
app.include_router(router)