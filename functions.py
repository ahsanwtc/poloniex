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

def structure_triangular_pairs(coin_list):
    # Variables
    triangular_pairs_list = []
    triangular_duplicates_list = []
    pairs_list = []

    # Get pair A
    for pair_a in coin_list:
        pair_a_split = pair_a.split('_')
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        # Put A in a Box
        a_pair_box = [a_base, a_quote]

        # Get pair B
        for pair_b in coin_list:
            pair_b_split = pair_b.split('_')
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            # Check pair B
            if pair_a != pair_b:
                # If it matches any coin in the pair a
                if b_base in a_pair_box or b_quote in a_pair_box:
                    pass
