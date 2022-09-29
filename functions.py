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
    # variables
    triangular_pairs_list = []
    triangular_duplicates_list = []
    pairs_list = coin_list[0:]

    # get pair A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split('_')
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        # put A in a Box
        a_pair_box = [a_base, a_quote]

        # get pair B
        for pair_b in pairs_list:
            pair_b_split = pair_b.split('_')
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            # check pair B
            if pair_a != pair_b:
                # If it matches any coin in the pair a
                if b_base in a_pair_box or b_quote in a_pair_box:

                    # check pair C
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split('_')
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]

                        # count the number of matching C items
                        if pair_c != pair_a and pair_c != pair_b:
                            combined = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            count_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    count_c_base += 1

                            count_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    count_c_quote += 1

                            # determining triangular match
                            if count_c_base == 2 and count_c_quote == 2 and c_base != c_quote:
                                concatenated = pair_a + ',' + pair_b + ',' + pair_c

                                # when different pairs are found with different configuration, sorted join will always
                                # result in a unique string which can be used to remove duplicates
                                # e.g. BTC_DASH USDT_BTC USDT_DASH and BTC_DASH USDT_DASH USDT_BTC are same duplicates
                                # unique_item string will help in excluding the duplicate
                                unique_item = ''.join(sorted(combined))
                                if unique_item not in triangular_duplicates_list:
                                    match_dict = {
                                        'a_base': a_base, 'b_base': b_base, 'c_base': c_base,
                                        'a_quote': a_quote, 'b_quote': b_quote, 'c_quote': c_quote,
                                        'pair_a': pair_a, 'pair_b': pair_b, 'pair_c': pair_c,
                                        'combined': concatenated
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    triangular_duplicates_list.append(unique_item)
    return triangular_pairs_list
