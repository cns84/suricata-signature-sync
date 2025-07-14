import requests
import os
import re

# Static known sources
static_feeds = {
    "ET Open": "https://rules.emergingthreats.net/open/suricata/emerging.rules",
    "TrafficID": "https://openinfosecfoundation.org/rules/trafficid/trafficid.rules",
    "Corelight": "https://feed.corelight.com/rules/corelight.rules",
    "CriticalPathSecurity": "https://raw.githubusercontent.com/CriticalPathSecurity/Suricata-Signatures/main/merged.rules",
    "SSLBL": "https://sslbl.abuse.ch/blacklist/sslblacklist.rules",
    "Open NRD": "https://downloads.stamus-networks.com/open-nrd/open-nrd.rules"
}

# GitHub search for public Suricata rules
github_search_url = "https://api.github.com/search/code?q=extension:rules+suricata+in:path"

headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "suricata-discovery-script"
}

output_dir = "discovered_rules"
os.makedirs(output_dir, exist_ok=True)

def fetch_static_feeds():
    for name, url in static_feeds.items():
        print(f"🔍 Fetching static feed: {name}")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                path = os.path.join(output_dir, f"{name.replace(' ', '_')}.rules")
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"✅ Saved: {path}")
            else:
                print(f"❌ Failed ({r.status_code}): {url}")
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")

def search_github_rules():
    print("\n🔎 Searching GitHub for Suricata rules...")
    try:
        r = requests.get(github_search_url, headers=headers, timeout=10)
        if r.status_code == 200:
            results = r.json().get("items", [])
            for item in results[:10]:  # Limit to first 10 for demo
                raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                filename = item["name"]
                print(f"📁 Found: {filename} from {item['repository']['full_name']}")
                try:
                    rule_data = requests.get(raw_url, timeout=10)
                    if rule_data.status_code == 200:
                        path = os.path.join(output_dir, f"github_{filename}")
                        with open(path, "wb") as f:
                            f.write(rule_data.content)
                        print(f"✅ Saved: {path}")
                    else:
                        print(f"❌ Failed to fetch raw rule: {raw_url}")
                except Exception as e:
                    print(f"❌ Error fetching GitHub rule: {e}")
        else:
            print(f"❌ GitHub search failed: {r.status_code}")
    except Exception as e:
        print(f"❌ GitHub API error: {e}")

# Run both discovery methods
fetch_static_feeds()
search_github_rules()