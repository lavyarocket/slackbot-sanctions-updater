from fetcher import download_sdn
from transformer import parse_sdn, to_json

raw = download_sdn()

cleaned = parse_sdn(raw)
json_output = to_json(cleaned)
with open("sdn.json", "w") as f:
    f.write(json_output)
