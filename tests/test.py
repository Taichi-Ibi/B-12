from utils import ConfigLoader
from api import Dify, Jina
import asyncio
from pprint import pprint

config_loader = ConfigLoader()
config = config_loader.get_config()


async def test():
    jina = Jina()
    res = await jina.search(query="Japan Capital")
    print(res)
    exit()
    dify = Dify(
        config=config,
        # app_name="summarizer",
        app_name="b_12",
        # app_name="thirdeye",
    )
    # async for response in dify.upload_file(
    #     "/Users/estyle-085/dev/B-12/data/image/名称未設定のデザイン (2).png",
    # ):
    #     print(response)
    # res = await dify.upload_file(
    #     "/Users/estyle-085/dev/B-12/data/image/名称未設定のデザイン (2).png",
    # )
    # print(res)
    # query = "猫の生態を教えて"
    query="リンゴは英語で？20文字以内で答えて"
    # query = "この画像はどこがイケてる？"
    # query = "もっとかっこよくするにはどこを変えたらいいかな"
    # print(query)
    # print (await dify.completion(query=query))
    async for stream in dify.chat(
        query=query,
        # conversation_id="7dd750ca-069c-4e95-8de5-d3cc9e275d41",
        # response_mode="blocking",
        response_mode="streaming",
        # files=[
        #     {
        #         "type": "image",
        #         "transfer_method": "local_file",
        #         "upload_file_id": "986ab777-9af2-45a1-949d-c113667f6000",
        #     }
        # ],
    ):
        pprint(stream)


if __name__ == "__main__":
    asyncio.run(test())
