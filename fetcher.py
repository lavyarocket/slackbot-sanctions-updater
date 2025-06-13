import requests

OFAC_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"

def download_sdn():
    r = requests.get(OFAC_URL, timeout=30)
    r.raise_for_status()
    return r.text
