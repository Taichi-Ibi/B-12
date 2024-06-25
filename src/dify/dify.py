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
        self.app = config.dify[app_name]
        self.headers = {
            "Authorization": f"Bearer {self.app.api_key}",
        }
        self.user_name = config.user_name

    def _filepath_to_content_type(self, filepath: str) -> str:
        image_extensions = {
            "png",
            "jpeg",
            "jpg",
            "webp",
            "gif",
        }
        if (extension := filepath.suffix.replace(".", "")) in image_extensions:
            content_type = f"image/{extension}"
        return content_type

    def _file_id_to_args(self, file_id: str):
        return {
            "type": "image",
            "transfer_method": "local_file",
            "upload_file_id": file_id,
        }

    async def completion(
        self, inputs: dict[str, str], files: list[dict[str, str]] = None
    ) -> str:
        end_point = "/completion-messages"
        headers = {**self.headers, "Content-Type": "application/json"}
        data = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": self.user_name,
            "files": files,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=Dify.base_url + end_point, headers=headers, json=data
            ) as response:
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
        if response_mode not in (response_modes := {"blocking", "streaming"}):
            raise ValueError(
                f"response_mode must be in {str(response_modes)}, but got '{response_mode}'"
            )
        if self.app.type == "agent" and response_mode == "blocking":
            raise NotImplementedError
        
        end_point = "/chat-messages"
        headers = {**self.headers, "Content-Type": "application/json"}
        data = {
            "inputs": inputs,
            "query": query,
            "response_mode": response_mode,
            "user": self.user_name,
            "conversation_id": conversation_id,
            "files": files,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=Dify.base_url + end_point, headers=headers, json=data
            ) as response:
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
        endpoint = "/files/upload"
        content_type = self._filepath_to_content_type(filepath=filepath)

        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field(
                name="file",
                value=filepath.read_bytes(),
                filename=filepath.name,
                content_type=content_type,
            )
            form.add_field(name="user", value=self.user_name)
            async with session.post(
                url=Dify.base_url + endpoint, headers=self.headers, data=form
            ) as response:
                if response.status != 201:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )
                return await response.json()
