import os
import requests
from zipfile import ZipFile
from io import BytesIO

FEEDS = {
    "community": "https://example.com/community-rules.zip",
    "emerging": "https://rules.emergingthreats.net/open/suricata-5.0/emerging.rules.tar.gz"
}

def download_and_extract(url, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch {url}")
        return

    if url.endswith(".zip"):
        with ZipFile(BytesIO(response.content)) as zf:
            zf.extractall(dest_dir)
    elif url.endswith(".tar.gz"):
        with open("temp_feed.tar.gz", "wb") as f:
            f.write(response.content)
        os.system(f"tar -xzf temp_feed.tar.gz -C {dest_dir}")
        os.remove("temp_feed.tar.gz")
    print(f"✅ Fetched and unpacked rules: {url}")

if __name__ == "__main__":
    for name, url in FEEDS.items():
        download_and_extract(url, f"rules/{name}")