from abc import ABC, abstractmethod
import logging

import discord

from src.utils import ConfigLoader

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
    async def handle_message(self, message, thread):
        pass