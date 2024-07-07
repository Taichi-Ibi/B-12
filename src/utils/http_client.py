"""
https://bocek.co.jp/media/formula/making-document/110/
https://www3.nhk.or.jp/news/
https://arxiv.org/pdf/1711.06769
https://www.irs.gov/pub/irs-pdf/f1040.pdf
https://www.mext.go.jp/content/20240611-ope_dev03-000036120-1.pdf
https://bocek.co.jp/media/wp-content/uploads/2024/04/prompty_banner_DL.png
https://x.com/Naoki_syakkin/status/1781989533128773901
"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from pypdf import PdfReader
from toolz import pipe

from .utils import IMAGE_DIR


@dataclass
class Contents:
    title: str = None
    text: str = None
    file_path: Path = None


class HttpClient:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self) -> None:
        self.save_dir: Path = Path(IMAGE_DIR)
        self.url: str = None
        self.content_type: str = None
        self.cotent: bytes = None

    async def curl(self, url: str) -> None:
        self.url = url
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=HttpClient.headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP status code {response.status}")
                self.content_type = response.headers["Content-Type"]
                self.content = await response.read()

    async def download_image(self, save_dir: str = None) -> Path:
        if save_dir is not None:
            self.save_dir = Path(save_dir)
        self.content_type.startswith("image")
        file_name = pipe(
            self.url.split("/")[-1],
            lambda x: Path(x).stem + "." + self.content_type.split("/")[-1],
        )
        file_path = self.save_dir / file_name
        file_path.write_bytes(self.content)
        return file_path.resolve()

    async def parse_content(self):
        # web page
        if self.content_type.startswith("text/html"):
            soup = BeautifulSoup(self.content, "html.parser")
            title = soup.find("title").text
            text = soup.find("body").get_text().strip()
            return Contents(title=title, text=text)
        # pdf
        elif self.content_type.endswith("pdf"):
            bytes_stream = BytesIO(self.content)
            reader = PdfReader(bytes_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            _title = "Title not found"
            title = pipe(
                reader.metadata.get("/Title", _title), lambda x: x if x else _title
            )
            return Contents(title=title, text=text.strip())
        elif self.content_type.startswith("image"):
            file_path = await self.download_image()
            return Contents(file_path=file_path)
        else:
            raise NotImplementedError(f"Unsupported content type: {self.content_type}")
