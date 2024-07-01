from src.discord_bot import ThirdEye
from src.api import Jina

if __name__ == "__main__":
    # bot = ThirdEye(bot_name="thirdeye")
    # bot.run()
    import json
    async def main():
        jina = Jina()
        # res = await jina.search(query="Mickey")
        res = await jina.read(url="https://x.com/rshosai/status/1783314550957433049")
        return res
    import asyncio
    res = asyncio.run(main())
    print(res)
    # print(res.keys())
    # for r in res:
        # print(r.title)
    # from pyperclip import copy
    # copy(res)
