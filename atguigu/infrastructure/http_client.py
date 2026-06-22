

import asyncio
from pprint import pprint

from httpx import AsyncClient

http_client: AsyncClient | None = None

def init_http_client():
	global http_client
	http_client = AsyncClient(timeout=120,trust_env=False)

async def dispose_http_client():
	await http_client.aclose()

async def main():
	init_http_client()

	response = await http_client.get(url="http://111.229.29.214:18081/orders/A20260410001")


	pprint(response.json())


if __name__ == '__main__':
	asyncio.run(main())
