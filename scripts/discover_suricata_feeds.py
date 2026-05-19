import requests
import os
import re

# Static known public feeds
STATIC_FEEDS = {
    "ET Open": "https://rules.emergingthreats.net/open/suricata-7.0.3/emerging-all.rules",
    "TrafficID": "https://openinfosecfoundation.org/rules/trafficid/trafficid.rules",
    "Corelight": "https://feed.corelight.com/rules/corelight.rules",
    #"CriticalPathSecurity": "https://raw.githubusercontent.com/CriticalPathSecurity/Suricata-Signatures/main/merged.rules",
    "SSLBL": "https://sslbl.abuse.ch/blacklist/sslblacklist.rules",
    #"Open NRD": "https://raw.githubusercontent.com/StamusNetworks/open-nrd-rules/main/open-nrd.rules.txt"
}

# GitHub search (requires token for rate-limit avoidance)
#GITHUB_SEARCH_URL = "https://api.github.com/search/code?q=extension:rules+suricata+in:path"
#GITHUB_TOKEN = os.getenv("GH_API_TOKEN")  # ✅ Set via GitHub Actions Secret
#
#HEADERS = {
#    "Accept": "application/vnd.github.v3+json",
#    "User-Agent": "suricata-feed-discovery"
#}
#if GITHUB_TOKEN:
#    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

OUTPUT_DIR = "discovered_rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_static_feeds():
    print("📡 Fetching static feeds...\n")
    for name, url in STATIC_FEEDS.items():
        try:
            print(f"🔍 {name}: {url}")
            response = requests.get(url, timeout=12)
            if response.status_code == 200:
                rule_text = response.text
                path = os.path.join(OUTPUT_DIR, f"{name.replace(' ', '_')}.rules")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(rule_text)
                rule_count = rule_text.count("alert ")
                print(f"   ✅ Saved {rule_count} rules to {path}\n")
            else:
                print(f"   ❌ HTTP {response.status_code}: {url}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")


def search_github_rules():
    print("🌐 Searching GitHub for Suricata .rules files...\n")
    try:
        r = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            items = r.json().get("items", [])
            print(f"🔎 Found {len(items)} rule candidates\n")
            for item in items[:10]:  # Limit for demo
                repo = item["repository"]["full_name"]
                filename = item["name"]
                raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                try:
                    content = requests.get(raw_url, timeout=10)
                    if content.status_code == 200:
                        clean_name = f"github_{repo.replace('/', '_')}_{filename}"
                        path = os.path.join(OUTPUT_DIR, clean_name)
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(content.text)
                        rule_count = content.text.count("alert ")
                        print(f"   ✅ Saved {rule_count} rules from {repo} → {path}")
                    else:
                        print(f"   ❌ Failed to fetch {raw_url} (HTTP {content.status_code})")
                except Exception as e:
                    print(f"   ❌ GitHub download error: {e}")
        else:
            print(f"❌ GitHub search error: HTTP {r.status_code}")
            if r.status_code == 401:
                print("   🔒 GitHub token may be missing or incorrect")
    except Exception as e:
        print(f"❌ GitHub API error: {e}")


# 🔁 Run both discovery flows
fetch_static_feeds()
search_github_rules()
