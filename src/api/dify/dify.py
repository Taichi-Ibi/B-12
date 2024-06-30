import aiohttp
from pathlib import Path
from typing import Any

import json

from src.utils import ConfigLoader

config_loader = ConfigLoader()
CONFIG = config_loader.get_config()


class Dify:
    base_url = "https://api.dify.ai/v1"

    def __init__(
        self,
        app_name: str,
    ) -> None:
        self.app = CONFIG.dify.get(app_name, None)
        self.headers = {
            "Authorization": f"Bearer {self.app.api_key}",
        }
        self.user_name = CONFIG.user_name

    def _filepath_to_content_type(self, filepath: Path) -> str:
        image_extensions = {
            "png",
            "jpeg",
            "jpg",
            "webp",
            "gif",
        }
        extension = filepath.suffix.replace(".", "")
        if extension in image_extensions:
            return f"image/{extension}"
        else:
            raise NotImplementedError

    async def _call_blocking(self, params: dict[str, Any], required_status: int):
        async with aiohttp.ClientSession() as session:
            async with session.post(**params) as response:
                if response.status == required_status:
                    return await response.json()
                else:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )

    async def _call_streaming(self, params: dict[str, Any], required_status: int):
        async with aiohttp.ClientSession() as session:
            async with session.post(**params) as response:
                if response.status == required_status:
                    async for chunk in response.content.iter_chunks():
                        lines = chunk[0].decode("utf-8").split("\n\n")
                        for line in lines:
                            try:
                                yield json.loads(line.replace("data: ", ""))
                            except json.JSONDecodeError:
                                continue
                else:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )

    async def completion(
        self,
        query: str,
        inputs: dict[str, str] = None,
        files: list[dict[str, str]] = None,
    ):
        params = {
            "url": Dify.base_url + "/completion-messages",
            "headers": {**self.headers, "Content-Type": "application/json"},
            "json": {
                "inputs": {"query": query, **(inputs if inputs is not None else {})},
                "response_mode": "blocking",
                "user": self.user_name,
                "files": files,
            },
        }
        return await self._call_blocking(params=params, required_status=200)

    async def chat(
        self,
        query: str,
        inputs: dict[str, str] = None,
        conversation_id: str = None,
        files: list[dict[str, str]] = None,
    ):
        params = {
            "url": Dify.base_url + "/chat-messages",
            "headers": {**self.headers, "Content-Type": "application/json"},
            "json": {
                "inputs": inputs,
                "query": query,
                "response_mode": "streaming",
                "user": self.user_name,
                "conversation_id": conversation_id,
                "files": files,
            },
        }
        async for response in self._call_streaming(params=params, required_status=200):
            yield response            

    async def upload_file(self, filepath: str):
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError

        form = aiohttp.FormData()
        form.add_field(
            name="file",
            value=filepath.read_bytes(),
            filename=filepath.name,
            content_type=self._filepath_to_content_type(filepath=filepath),
        )
        form.add_field(name="user", value=self.user_name)

        params = {
            "url": Dify.base_url + "/files/upload",
            "headers": self.headers,
            "data": form,
        }
        return await self._call_blocking(params=params, required_status=201)