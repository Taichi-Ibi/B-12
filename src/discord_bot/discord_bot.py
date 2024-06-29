from abc import ABC, abstractmethod

import discord

from src.utils import find_urls
from src.utils import ConfigLoader

config_loader = ConfigLoader()
CONFIG = config_loader.get_config()


class DiscordBot(ABC):
    @property
    @abstractmethod
    def token(self):
        pass

    def __init__(self):
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

    def run(self):
        self.client.run(self.token)

    @abstractmethod
    async def handle_message(self, message):
        pass


class ThirdEye(DiscordBot):
    @property
    def token(self):
        return CONFIG.discord.thirdeye.api_key

    async def handle_message(self, message):
        thread_name = "New Thread"
        thread = await message.create_thread(name=thread_name)
        content = message.content
        urls = find_urls(text=content)
        if urls:
            for url in urls:
                await thread.send(url)
