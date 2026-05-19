import requests
import os
import tarfile

# Comments

# URL to the compressed rules archive
url = "https://rules.pawpatrules.fr/suricata/paw-patrules.tar.gz"

# Local file paths
output_dir = "rules"
archive_path = "paw-patrules.tar.gz"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Download the tar.gz archive
print(f"Downloading: {url}")
response = requests.get(url, stream=True)

if response.status_code == 200:
    with open(archive_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")
else:
    print(f"Failed to download: {response.status_code}")
    exit(1)

# Extract .rules files from archive
with tarfile.open(archive_path, "r:gz") as tar:
    for member in tar.getmembers():
        if member.name.endswith(".rules"):
            member.name = os.path.basename(member.name)  # Avoid path traversal
            tar.extract(member, output_dir)
            print(f"Extracted: {member.name}")

# Clean up the archive file
os.remove(archive_path)
print("Archive cleaned up.")
