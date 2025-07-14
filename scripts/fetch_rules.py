import requests
import os

sources = [
    "https://feed.corelight.com/rules/corelight.rules",
    "https://openinfosecfoundation.org/rules/trafficid/trafficid.rules"
]

output_dir = "rules"
os.makedirs(output_dir, exist_ok=True)

combined_path = os.path.join(output_dir, "combined.rules")
downloaded = 0
failed = 0

with open(combined_path, "wb") as combined:
    for url in sources:
        print(f"🔄 Fetching: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            combined.write(response.content + b"\n")
            print(f"✅ Successfully downloaded from: {url}")
            downloaded += 1
        else:
            print(f"❌ Failed to fetch {url}: {response.status_code}")
            failed += 1

print(f"\n📦 Completed rule fetch:")
print(f"   ✔ Downloads: {downloaded}")
print(f"   ❌ Failures: {failed}")
print(f"   📁 Merged output: {combined_path}")