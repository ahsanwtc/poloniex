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
    # Variables
    triangular_pairs_list = []
    triangular_duplicates_list = []
    pairs_list = []

    # Get pair A
    for pair_a in coin_list:
        pair_a_split = pair_a.split('_')
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        print(pair_a_split)

    return triangular_pairs_list


""" MAIN """
if __name__ == '__main__':
    coin_list = step_0()
    structured_pairs = step_1(coin_list)
