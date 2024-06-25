import aiohttp
from pathlib import Path

from dotmap import DotMap
import json


class Dify:
    base_url = "https://api.dify.ai/v1"

    def __init__(
        self,
        app_name: str,
        config: DotMap,
    ) -> None:
        self.app = config.dify.get(app_name, None)
        self.headers = {
            "Authorization": f"Bearer {self.app.api_key}",
        }
        self.user_name = config.user_name

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

    async def completion(
        self,
        query: str,
        inputs: dict[str, str] = None,
        files: list[dict[str, str]] = None,
    ) -> str:
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

        async with aiohttp.ClientSession() as session:
            async with session.post(**params) as response:
                if response.status != 200:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )
                return await response.json()

    async def chat(
        self,
        query: str,
        inputs: dict[str, str] = None,
        conversation_id: str = None,
        files: list[dict[str, str]] = None,
        response_mode: str = "blocking",
    ) -> str:
        # check args
        response_modes = {"blocking", "streaming"}
        if response_mode not in response_modes:
            raise ValueError(
                f"response_mode must be in {str(response_modes)}, but got '{response_mode}'"
            )
        if self.app.type == "agent" and response_mode == "blocking":
            raise NotImplementedError

        params = {
            "url": Dify.base_url + "/chat-messages",
            "headers": {**self.headers, "Content-Type": "application/json"},
            "json": {
                "inputs": inputs,
                "query": query,
                "response_mode": response_mode,
                "user": self.user_name,
                "conversation_id": conversation_id,
                "files": files,
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(**params) as response:
                if response.status != 200:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )
                async for chunk in response.content.iter_chunks():
                    lines = chunk[0].decode("utf-8").split("\n\n")
                    for line in lines:
                        try:
                            yield json.loads(line.replace("data: ", ""))
                        except json.JSONDecodeError:
                            continue

    async def upload_file(self, filepath: Path):
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

        async with aiohttp.ClientSession() as session:
            async with session.post(**params) as response:
                if response.status != 201:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )
                return await response.json()
