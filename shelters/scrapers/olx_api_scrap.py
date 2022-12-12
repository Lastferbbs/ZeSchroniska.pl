import requests
from headers import headers
import re


content = requests.get(
    "https://www.olx.pl/d/elektronika/gry-konsole/konsole/playstation/bydgoszcz/q-ps4/?search%5Bfilter_float_price:to%5D=1000&search%5Bfilter_enum_state%5D%5B0%5D=used",
    headers=headers,
).content


api_link = re.findall(r"first\\.*?spell_checker", str(content))
api_link = api_link[0][12:].replace("\\\\", "\\").replace("u002F", "")
print(api_link.replace("\\\\", "\\")[:-1])
debug = 1
