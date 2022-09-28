# STEP 0: Gather correct coins

"""
    STEP 0: Finding coins which can be traded
    Exchange: Poloniex
    https://docs.poloniex.com/#introduction
"""

import requests
import json

url = 'https://poloniex.com/public?command=returnTicker'
req = requests.get(url)
response_json = json.loads(req.text)
print(response_json)