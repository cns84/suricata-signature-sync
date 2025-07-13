config_content = """%YAML 1.1
---
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16]"
    EXTERNAL_NET: "[8.8.8.8, 1.1.1.1]"
    DNS_SERVERS: "[192.168.0.53]"
    SMTP_SERVERS: "[192.168.0.25]"
    HTTP_SERVERS: "[192.168.0.80]"
    SQL_SERVERS: "[192.168.0.143]"
    SHELLCODE_SERVERS: "[192.168.0.200]"
    SIP_SERVERS: "[192.168.0.5060]"
    AIM_SERVERS: "[192.168.0.4099]"
default-rule-path: rules
default-log-dir: /tmp/suricata-logs
"""

with open("/tmp/suricata.yaml", "w") as f:
    f.write(config_content)
print("Suricata config written to /tmp/suricata.yaml")
