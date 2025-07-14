import re

# Step 1: Define base config
config_lines = [
    "%YAML 1.1",
    "---",
    "vars:",
    "  address-groups:",
    '    HOME_NET: "[192.168.1.0/24]"',
    '    EXTERNAL_NET: "[8.8.8.8, 1.1.1.1]"',
    '    HTTP_SERVERS: "[192.168.1.10]"',
    '    DNS_SERVERS: "[192.168.1.53]"',
    '    SMTP_SERVERS: "[192.168.1.25]"',
    '    SQL_SERVERS: "[192.168.1.143]"',
    '    SHELLCODE_SERVERS: "[192.168.1.200]"',
    '    SIP_SERVERS: "[192.168.1.60]"',
    '    AIM_SERVERS: "[192.168.1.99]"'
]

# Step 2: Scan combined.rules for additional port variables
port_variable_pattern = re.compile(r"\$(\w+_PORTS)\b")
rules_file = "rules/combined.rules"
port_vars_found = set()

try:
    with open(rules_file, "r") as f:
        for line in f:
            for match in port_variable_pattern.findall(line):
                port_vars_found.add(match)
    print(f"🔍 Detected port variables: {sorted(port_vars_found)}")
except FileNotFoundError:
    print("❌ combined.rules not found. Skipping variable scan.")

# Step 3: Define safe defaults for any missing ports
default_ports = {
    "HTTP_PORTS": "[80,443,8080,8000]",
    "SMTP_PORTS": "[25,587]",
    "SQL_PORTS": "[1433,3306]",
    "DNS_PORTS": "[53]",
    "SIP_PORTS": "[5060]",
    "AIM_PORTS": "[4099]",
    "FTP_PORTS": "[21]",
    "IRC_PORTS": "[6667]",
    "TELNET_PORTS": "[23]",
    "RDP_PORTS": "[3389]"
}

for var in sorted(port_vars_found):
    config_lines.append(f'    {var}: {default_ports.get(var, "[1]")}')

config_lines.append("default-rule-path: rules")
config_lines.append("default-log-dir: /tmp/suricata-logs")

# Step 4: Write config file
import re

# Step 1: Define base config
config_lines = [
    "%YAML 1.1",
    "---",
    "vars:",
    "  address-groups:",
    '    HOME_NET: "[192.168.1.0/24]"',
    '    EXTERNAL_NET: "[8.8.8.8, 1.1.1.1]"',
    '    HTTP_SERVERS: "[192.168.1.10]"',
    '    DNS_SERVERS: "[192.168.1.53]"',
    '    SMTP_SERVERS: "[192.168.1.25]"',
    '    SQL_SERVERS: "[192.168.1.143]"',
    '    SHELLCODE_SERVERS: "[192.168.1.200]"',
    '    SIP_SERVERS: "[192.168.1.60]"',
    '    AIM_SERVERS: "[192.168.1.99]"'
]

# Step 2: Scan combined.rules for additional port variables
port_variable_pattern = re.compile(r"\$(\w+_PORTS)\b")
rules_file = "rules/combined.rules"
port_vars_found = set()

try:
    with open(rules_file, "r") as f:
        for line in f:
            for match in port_variable_pattern.findall(line):
                port_vars_found.add(match)
except FileNotFoundError:
    print("❌ combined.rules not found. Skipping variable scan.")

# Step 3: Define safe defaults for any missing ports
default_ports = {
    "HTTP_PORTS": "[80,443,8080,8000]",
    "SMTP_PORTS": "[25,587]",
    "SQL_PORTS": "[1433,3306]",
    "DNS_PORTS": "[53]",
    "SIP_PORTS": "[5060]",
    "AIM_PORTS": "[4099]",
    "FTP_PORTS": "[21]",
    "IRC_PORTS": "[6667]",
    "TELNET_PORTS": "[23]",
    "RDP_PORTS": "[3389]"
}

for var in sorted(port_vars_found):
    config_lines.append(f'    {var}: {default_ports.get(var, "[1]")}')

config_lines.append("default-rule-path: rules")
config_lines.append("default-log-dir: /tmp/suricata-logs")

# Step 4: Write config file
with open("/tmp/suricata.yaml", "w") as f:
    f.write("\n".join(config_lines))

print(f"✔ Suricata config generated with {len(port_vars_found)} auto-detected port variables.")