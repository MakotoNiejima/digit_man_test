import uvicorn

from atguigu.api.app import app
from atguigu.config.settings import settings

if __name__ == '__main__':
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)