from pathlib import Path
import re
import shutil

IMAGE_DIR = "./data/image"

def find_urls(text: str) -> list[str]:
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )
    return urls


def metadata_to_link(app_name: str, conversation_id: str):
    return f"[{app_name}](https://{conversation_id})"


def link_to_metadata(input_str) -> tuple[str, str]:
    match = re.match(r"\[(.*?)\]\(https://(.*?)\)", input_str)
    if match:
        text = match.group(1)
        url = match.group(2)
        return text, url
    else:
        return None, None


def empty_directory(directory_path: str = IMAGE_DIR):
    directory_path = Path(directory_path)
    # ディレクトリが存在するか確認
    if not directory_path.exists():
        print(f"指定されたディレクトリは存在しません: {directory_path}")
        return

    # ディレクトリ内のすべての項目を確認
    for item in directory_path.iterdir():
        # .から始まるファイルはスキップ
        if item.name.startswith("."):
            continue

        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"エラー: {item} を削除できませんでした。理由: {e}")
