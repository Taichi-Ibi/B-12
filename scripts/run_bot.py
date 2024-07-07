from src.discord_bot import B12Bot
# from src.api import Jina

if __name__ == "__main__":
    bot = B12Bot(bot_name="thirdeye")
    bot.run()
    # import json
    # async def main():
    #     jina = Jina()
    #     # res = await jina.search(query="Mickey")
    #     # url = "https://x.com/TJO_datasci/status/1807348227722674470"
    #     url = "https://x.com/rshosai/status/1783314550957433049"
    #     res = await jina.read(url=url)
    #     return res
    # import asyncio
    # res = asyncio.run(main())
    # print(res)
    # print(res.keys())
    # for r in res:
        # print(r.title)
    # from pyperclip import copy
    # print(res.title)
    # print(res.content)
    # copy(res.content)
