from abc import ABC, abstractmethod
import logging

import discord

from src.api import Dify
from src.utils import ConfigLoader, find_urls, HttpClient

logging.basicConfig(level=logging.INFO)
config_loader = ConfigLoader()
CONFIG = config_loader.get_config()


class DiscordBot(ABC):

    def __init__(self, bot_name):
        self.bot_name = bot_name
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            print(f"We have logged in as {self.client.user}")

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            await self.handle_message(message=message)

    @property
    def token(self):
        bot = CONFIG.discord.get(self.bot_name, None)
        if bot is None:
            raise ValueError
        return bot.api_key

    def run(self):
        self.client.run(self.token)

    @abstractmethod
    async def handle_message(self, message):
        pass


class ThirdEye(DiscordBot):
    """
    TODO
    - Chat対応
    - imageとpdfの対応
    """

    async def handle_message(self, message):
        # fetch url
        urls = find_urls(text=message.content)
        if not urls:
            return
        client = HttpClient()
        await client.curl(url=urls[0])

        # parse content
        contents = await client.parse_content()

        # create thread
        thread = await message.create_thread(name=contents.title)

        # respond
        journalist = Dify(app_name="journalist")
        answer = ""
        async for chunk in journalist.chat(query=contents.text):
            event = chunk.get("event", None)
            if event in {"message", "agent_message"}:
                answer += chunk["answer"]
        await thread.send(answer.strip())
