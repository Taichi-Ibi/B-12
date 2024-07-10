from pathlib import Path
from typing import Optional

import discord

from .discord_bot import DiscordBot
from src.api import Dify
from src.utils import find_urls, HttpClient, link_to_metadata, metadata_to_link, empty_directory


def prep_files(file_id: str):
    files = [
        {
            "type": "image",
            "transfer_method": "local_file",
            "upload_file_id": file_id,
        }
    ]
    return files


class BotCaller:
    def __init__(self, message: str):
        self.message = message
        self._thread: Optional[discord.threads.Thread] = None
        self._app_name: Optional[str] = None
        self._conversation_id: Optional[str] = None

    async def resume(self):
        if isinstance(self.message.channel, discord.threads.Thread):
            self._thread = self.message.channel
            history = [
                h async for h in self._thread.history(limit=2, oldest_first=True)
            ]
            if len(history) >= 2:
                self._app_name, self._conversation_id = link_to_metadata(
                    input_str=history[1].content
                )

    def set_app_name(self, value: str):
        self._app_name = value

    async def _handle_stream(self, stream_response) -> tuple[str, str]:
        answer = ""
        conversation_id = None
        async for chunk in stream_response:
            event = chunk.get("event", None)
            if conversation_id is None:
                conversation_id = chunk.get("conversation_id", None)
            if event in {"message", "agent_message"}:
                answer += chunk["answer"]
        # 初回のメッセージ
        if self._conversation_id is None:
            metadata = metadata_to_link(
                app_name=self._app_name, conversation_id=conversation_id
            )
        # 2ターン目以降
        else:
            metadata = None
        answer = answer.strip()
        return metadata, answer

    async def _thread_send(self, metadata, answer):
        if metadata is not None:
            await self._thread.send(metadata)
        await self._thread.send(answer)

    async def b12(self):
        dify = Dify(app_name=self._app_name)

        # create thread
        if self._thread is None:
            summarizer = Dify(app_name="summarizer")
            response = await summarizer.completion(query=self.message.content)
            self._thread = await self.message.create_thread(name=response["answer"])

        # response
        stream_response = dify.chat(
            query=self.message.content, conversation_id=self._conversation_id
        )
        response = await self._handle_stream(stream_response=stream_response)
        await self._thread_send(*response)

    async def journalist(self):
        dify = Dify(app_name=self._app_name)

        # start conversation
        if self._thread is None:
            urls = find_urls(text=self.message.content)
            client = HttpClient()
            await client.curl(url=urls[0])
            contents = await client.parse_content()
            # create thread
            self._thread = await self.message.create_thread(name=contents.title)
            # api call
            stream_response = dify.chat(query=contents.text)

        # continue conversation
        else:
            # api call
            stream_response = dify.chat(
                query=self.message.content, conversation_id=self._conversation_id
            )

        # respond
        response = await self._handle_stream(stream_response=stream_response)
        await self._thread_send(*response)

    async def thirdeye(self):
        dify = Dify(app_name=self._app_name)

        # 初回
        if self._thread is None:
            answers = []
            for i, attachment in enumerate(self.message.attachments):
                if self._thread is None:
                    # create thread
                    self._thread = await self.message.create_thread(
                        name="Processing image ..."
                    )                
                # parse content
                client = HttpClient()
                await client.curl(url=attachment.url)
                contents = await client.parse_content()

                # describe image
                response = await dify.upload_file(filepath=contents.file_path)
                empty_directory()
                if self.message.content:
                    query = self.message.content
                else:
                    query = "No message provided."
                print(query)
                stream_response = dify.chat(
                    query=query,
                    conversation_id=self._conversation_id,
                    files=prep_files(file_id=response["id"]),
                )
                metadata, answer = await self._handle_stream(
                    stream_response=stream_response
                )
                answer_w_filename = f"> {contents.file_path.name}\n\n{answer}"
                answers.append(answer_w_filename)
                if i == 0:
                    await self._thread.send(metadata)
                    _, self._conversation_id = link_to_metadata(input_str=metadata)
                await self._thread.send(answer_w_filename)
            # summarize
            whole_answer = "\n\n".join(answers)
            summarizer = Dify(app_name="summarizer")
            response = await summarizer.completion(query=whole_answer)
            await self._thread.edit(name=response["answer"])

        # 2ターン目以降
        else:
            stream_response = dify.chat(
                query=self.message.content, conversation_id=self._conversation_id
            )
            response = await self._handle_stream(stream_response=stream_response)
            await self._thread_send(*response)

    async def call(self):
        if self._app_name == "b12":
            await self.b12()
        elif self._app_name == "journalist":
            await self.journalist()
        elif self._app_name == "thirdeye":
            await self.thirdeye()


class B12Bot(DiscordBot):

    async def handle_message(self, message):
        try:
            async with message.channel.typing():
                # set bot state
                bot_caller = BotCaller(message=message)
                await bot_caller.resume()
                if bot_caller._app_name is None:
                    if message.attachments:
                        bot_caller.set_app_name("thirdeye")
                    elif find_urls(message.content):
                        bot_caller.set_app_name("journalist")
                    else:
                        bot_caller.set_app_name("b12")
            await bot_caller.call()
        except Exception as e:
            await message.channel.send(f"error: {e}")
