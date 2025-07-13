import requests
import os

sources = [
    "https://feed.corelight.com/rules/corelight.rules",
    #"https://openinfosecfoundation.org/rules/trafficid/trafficid.rules"
]

output_dir = "rules"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "combined.rules"), "wb") as combined:
    for url in sources:
        print(f"Downloading: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            combined.write(response.content + b"\n")
        else:
            print(f"Failed to fetch {url}: {response.status_code}")