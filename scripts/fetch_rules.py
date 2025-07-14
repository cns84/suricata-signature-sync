import requests
import os

# 🧭 Define rule sources with display names
sources = {
    "Corelight": "https://feed.corelight.com/rules/corelight.rules",
    "TrafficID": "https://openinfosecfoundation.org/rules/trafficid/trafficid.rules",
    "CriticalPathSecurity": "https://raw.githubusercontent.com/CriticalPathSecurity/Suricata-Signatures/main/merged.rules",
    "SSLBL (Abuse.ch)": "https://sslbl.abuse.ch/blacklist/sslblacklist.rules",
    "Open NRD (Stamus)": "https://downloads.stamus-networks.com/open-nrd/open-nrd.rules"
}

output_dir = "rules"
os.makedirs(output_dir, exist_ok=True)

combined_path = os.path.join(output_dir, "combined.rules")
downloaded = 0
failed = 0

with open(combined_path, "wb") as combined:
    for name, url in sources.items():
        print(f"🔄 Fetching [{name}] from {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                combined.write(response.content + b"\n")
                print(f"✅ Fetched rules from: {name}")
                downloaded += 1
            else:
                print(f"❌ Failed to fetch [{name}]: HTTP {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"❌ Error fetching [{name}]: {e}")
            failed += 1

# 📦 Summary
print("\n📊 Rule Fetch Summary:")
print(f"   ✔ Downloads: {downloaded}")
print(f"   ❌ Failures: {failed}")
print(f"   📁 Merged to: {combined_path}")