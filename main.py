import json

import functions

"""
    STEP 0: Finding coins which can be traded
    Exchange: Poloniex
    https://docs.poloniex.com/#introduction
"""
def step_0():
    # Extract list of coins and prices from Exchange
    response_json = functions.get_coin_tickers('https://poloniex.com/public?command=returnTicker')

    # Loop through each object and find the tradeable pairs
    return functions.collect_tradeables(response_json)


"""
    STEP 1: Structuring triangular pairs
    Calculation only
"""
def step_1(unstructured_list):
    # structure the list of tradeable triangular arbitrage pairs
    structured_list = functions.structure_triangular_pairs(unstructured_list)

    # export list to json file
    with open('data/structured-triangular-pairs.json', 'w') as fp:
        json.dump(structured_list, fp)


""" MAIN """
if __name__ == '__main__':
    coin_list = step_0()
    step_1(coin_list)
