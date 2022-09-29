import requests
import json


# Get list of coins and prices from Exchange
def get_coin_tickers(url):
    req = requests.get(url)
    return json.loads(req.text)


# Loop through each object and find the tradeable pairs
def collect_tradeables(token_list):
    coin_list = []
    for coin in token_list:
        is_frozen = token_list[coin]['isFrozen']
        is_post_only = token_list[coin]['postOnly']
        if is_frozen == '0' and is_post_only == '0':
            coin_list.append(coin)
    return coin_list
