import re

import aiohttp
from bs4 import BeautifulSoup

def find_urls(text: str) -> list[str]:
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )
    return urls


async def curl(url: str) -> dict[str, str | bytes]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"HTTP status code {response.status}")
            content_type = response.headers.get("Content-Type", None)
            return {"content_type": content_type, "content": await response.read()}


def web_browsing(content: bytes) -> dict[str, str]:
    soup = BeautifulSoup(content, "html.parser")
    title = soup.find("title").text
    text = soup.find("body").get_text()
    return {"title": title, "text": text}


# async def main():
#     # url = "https://bocek.co.jp/media/formula/making-document/110/"
#     url = "https://www3.nhk.or.jp/news/"
#     #     url = "https://arxiv.org/pdf/1711.06769"
#     #     url = "https://bocek.co.jp/media/wp-content/uploads/2024/04/prompty_banner_DL.png"
#     res = await curl(url=url)
#     web_content = web_browsing(content=res["content"])
#     print(web_content["text"])
#     # print(res["content_type"])


# import asyncio

# asyncio.run(main())
# # browsing("")
