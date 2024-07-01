import aiohttp
from dataclasses import dataclass
from urllib.parse import quote

import json

from src.utils import ConfigLoader

config_loader = ConfigLoader()
CONFIG = config_loader.get_config()

@dataclass
class JinaData:
    title: str
    content: str
    url: str
    description: str = None
    publishedTime: str = None

class Jina:
    def __init__(
        self,
    ) -> None:
        self.app = CONFIG.jina

    async def _call_api(self, url: str, required_status: int):
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.app.api_key}",
                "Accept": "application/json",
                "X-Return-Format": "markdown"
                }
            async with session.get(url, headers=headers) as response:
                if response.status == required_status:
                    return await response.text()
                else:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )

    async def read(self, url: str) -> JinaData:
        url = "https://r.jina.ai/" + url
        res = await self._call_api(url=url, required_status=200)
        return JinaData(**json.loads(res)["data"])

    async def search(self, query: str) -> list[JinaData]:
        url = "https://s.jina.ai/" + quote(query)
        res = await self._call_api(url=url, required_status=200)
        return [JinaData(**r) for r in json.loads(res)["data"]]