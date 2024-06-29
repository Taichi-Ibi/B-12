from abc import ABC, abstractmethod

import discord

class DiscordBot(ABC):
    def __init__(self, token):
        self.token = token
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            print(f'We have logged in as {self.client.user}')
        
        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            await self.reply(message=message)

    def run(self):
        self.client.run(self.token)

    @abstractmethod
    async def reply(self, message):
        pass

class ThirdEye(DiscordBot):
    async def reply(self, message):
        thread_name = "New Thread"
        thread = await message.create_thread(name=thread_name)
        content = message.content
        await thread.send(content)

# 使用例
if __name__ == "__main__":
    bot = ThirdEye('MTI1NDAxNTk2MDQwNzM0MzE1NA.GqsmsF.sxaoQB4HS0jQcTA5oeDQeNU8uiBF-We5H_8Cp8')
    bot.run()
