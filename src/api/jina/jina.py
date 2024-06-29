import aiohttp

from utils import ConfigLoader

config_loader = ConfigLoader()
CONFIG = config_loader.get_config()


class Jina:
    def __init__(
        self,
    ) -> None:
        self.app = CONFIG.jina

    async def _call_api(self, url: str, required_status: int):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.app.api_key}"}
            async with session.get(url, headers=headers) as response:
                if response.status == required_status:
                    return await response.text()
                else:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )

    async def read(self, url: str) -> str:
        base_url = "https://r.jina.ai/"
        return await self._call_api(url=base_url + url, required_status=200)

    async def search(self, query: str) -> str:
        base_url = "https://s.jina.ai/"
        return await self._call_api(url=base_url + query, required_status=200)
