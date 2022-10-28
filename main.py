import json
import functions
import time

# Set variables
coin_price_url = 'https://poloniex.com/public?command=returnTicker'

"""
    STEP 0: Finding coins which can be traded
    Exchange: Poloniex
    https://docs.poloniex.com/#introduction
"""
def step_0():
    # Extract list of coins and prices from Exchange
    response_json = functions.get_coin_tickers(coin_price_url)

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


"""
    STEP 2: Calculate surface Arbitrage oppertunities
    Exchange: Poloniex
    https://docs.poloniex.com/#introduction
"""
def step_2():
    # Get structured pairs
    with open('data/structured-triangular-pairs.json') as json_file:
        structured_pairs = json.load(json_file)

    # Get latest surface prices
    prices_json = functions.get_coin_tickers(coin_price_url)

    # Loop through and get structured price information
    for t_pair in structured_pairs:
        time.sleep(0.3)
        prices_dictionary = functions.get_price_for_t_pair(t_pair, prices_json)
        surface_arbitrage = functions.cal_triangular_arbitrage_surface_rate(t_pair, prices_dictionary)
        if len(surface_arbitrage) > 0:
            real_rate_arbitrage = functions.get_depth_from_orderbook(surface_arbitrage)
            print(real_rate_arbitrage)
            time.sleep(1)


""" MAIN """
if __name__ == '__main__':
    # coin_list = step_0()
    # step_1(coin_list)
    step_2()
