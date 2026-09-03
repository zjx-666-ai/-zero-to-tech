

import requests
import json

ip = requests.get("https://ip.3322.net", timeout=10).text.strip()
print(json.dumps({"ip": ip}))
