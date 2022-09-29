# STEP 0: Gather correct coins

"""
    STEP 0: Finding coins which can be traded
    Exchange: Poloniex
    https://docs.poloniex.com/#introduction
"""
import functions

# Extract list of coins and prices from Exchange
response_json = functions.get_coin_tickers('https://poloniex.com/public?command=returnTicker')

# Loop through each object and find the tradeable pairs
coin_list = functions.collect_tradeables(response_json)

print(coin_list)