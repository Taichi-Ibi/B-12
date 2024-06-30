from io import BytesIO
from pathlib import Path
import re

import aiohttp
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from toolz import pipe
from pypdf import PdfReader


def find_urls(text: str) -> list[str]:
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )
    return urls


class HttpClient:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self) -> None:
        self.save_dir = Path("./data/image")
        self.url: str = None
        self.content_type: str = None
        self.cotent: bytes = None

    def _remove_bom(self, text: str):
        if text.startswith("\ufeff"):
            return text.lstrip("\ufeff")
        else:
            return text

    async def curl(self, url: str) -> None:
        self.url = url
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=HttpClient.headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP status code {response.status}")
                self.content_type = response.headers["Content-Type"]
                self.content = await response.read()

    async def save_image(self, save_dir: str = None) -> Path:
        if save_dir is not None:
            self.save_dir = Path(save_dir)
        self.content_type.startswith("image")
        file_name = Path(self.url).name
        file_path = self.save_dir / file_name
        with open(file_path, "wb") as f:
            f.write(self.content)
        return file_path.resolve()

    async def parse_content(self):
        """TODO pdfにも対応する"""
        # web page
        if self.content_type.startswith("text/html"):
            soup = BeautifulSoup(self.content, "html.parser")
            title = soup.find("title").text
            text = soup.find("body").get_text().strip()
            return {"title": title, "text": text}
        # pdf
        elif self.content_type.endswith("pdf"):
            bytes_stream = BytesIO(self.content)
            reader = PdfReader(bytes_stream)
            text = ""
            for page in reader.pages:
                page = reader.pages[0]
                text += page.extract_text()
            _title = "Title not found"
            title = pipe(
                reader.metadata.get("/Title", _title), lambda x: x if x else _title
            )
            return {"title": title, "text": text.strip()}


async def main():
    # url = "https://bocek.co.jp/media/formula/making-document/110/"
    # url = "https://www3.nhk.or.jp/news/"
    # url = "https://arxiv.org/pdf/1711.06769"
    # url = "https://www.irs.gov/pub/irs-pdf/f1040.pdf"
    url = "https://www.mext.go.jp/content/20240611-ope_dev03-000036120-1.pdf"
    # url = "https://bocek.co.jp/media/wp-content/uploads/2024/04/prompty_banner_DL.png"
    client = HttpClient()
    await client.curl(url=url)
    res = await client.parse_content()
    # path = await web.save_image()
    # print(path)
    # res = await client.read_text()
    # print(res["text"][:100])
    # print(web.content_type)
    # res = await curl(url=url)
    # file_path = save_image(res)


#     web_content = web_browsing(content=res["content"])
#     print(web_content["text"])
#     # print(res["content_type"])


import asyncio

asyncio.run(main())
# # browsing("")
