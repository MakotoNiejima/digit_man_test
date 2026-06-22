"""
llm客户端
"""
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from atguigu.config.settings import settings


llm_client: BaseChatModel = init_chat_model(
	model=settings.llm_model,
	model_provider="openai",
	base_url=settings.llm_base_url,
	api_key=settings.llm_api_key,
	temperature=0,
	timeout=120
)



if __name__ == '__main__':
    response=llm_client.invoke("哈哈哈哈")
    print(response.content)