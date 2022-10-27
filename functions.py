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

# Structured prices
def get_price_for_t_pair(t_pair, prices_json):
    # Extract pair info
    pair_a = t_pair['pair_a']
    pair_b = t_pair['pair_b']
    pair_c = t_pair['pair_c']

    # Extract price information for the given pairs
    pair_a_ask = float(prices_json[pair_a]['lowestAsk'])
    pair_a_bid = float(prices_json[pair_a]['highestBid'])
    pair_b_ask = float(prices_json[pair_b]['lowestAsk'])
    pair_b_bid = float(prices_json[pair_b]['highestBid'])
    pair_c_ask = float(prices_json[pair_c]['lowestAsk'])
    pair_c_bid = float(prices_json[pair_c]['highestBid'])

    # Return dictionary
    return {
        'pair_a_ask': pair_a_ask,
        'pair_a_bid': pair_a_bid,
        'pair_b_ask': pair_b_ask,
        'pair_b_bid': pair_b_bid,
        'pair_c_ask': pair_c_ask,
        'pair_c_bid': pair_c_bid
    }

# Calculate surface arbitrage opportunity
def cal_triangular_arbitrage_surface_rate(t_pair, prices_dictionary):
    # Set variables
    starting_amount = 1
    min_surface_rate = 0
    surface_dictionary = {}
    contract_1 = ''
    contract_2 = ''
    contract_3 = ''
    direction_trade_1 = ''
    direction_trade_2 = ''
    direction_trade_3 = ''
    acquired_coin_t1 = 0
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = False # calculated will be True if trades are finished and need to break out of current iteration

    # Extract pair variables
    a_base = t_pair['a_base']
    a_quote = t_pair['a_quote']
    b_base = t_pair['b_base']
    b_quote = t_pair['b_quote']
    c_base = t_pair['c_base']
    c_quote = t_pair['c_quote']
    pair_a = t_pair['pair_a']
    pair_b = t_pair['pair_b']
    pair_c = t_pair['pair_c']

    # Extract price information
    a_ask = prices_dictionary['pair_a_ask']
    a_bid = prices_dictionary['pair_a_bid']
    b_ask = prices_dictionary['pair_b_ask']
    b_bid = prices_dictionary['pair_b_bid']
    c_ask = prices_dictionary['pair_c_ask']
    c_bid = prices_dictionary['pair_c_bid']

    # Set directions and loop through
    direction_list = ['forward', 'reverse']
    for direction in direction_list:
        # Set additional variables for swap information
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        """
            Poloniex Rules !!
            If we are swapping the coin on the left (Base) to the right (Quote) then * (1 / Ask)
            If we are swapping the coin on the right (Quote) to the left (Base) then * Bid
        """

        # Assume starting with a_base and swapping for q_quote
        if direction == 'forward':
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = 1 / a_ask
            direction_trade_1 = 'base_to_quote'

        if direction == 'reverse':
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            direction_trade_1 = 'quote_to_base'

        # Place first trade
        acquired_coin_t1 = starting_amount * swap_1_rate

        # First leg of the trade
        contract_1 = pair_a

        """
            USDT_BTC | BTC_ETH | USDT_ETH
            USDT_BTC | ETH_BTC | USDT_ETH
            USDT_BTC | ETH_BTC | ETH_USDT 
            ...
            ...
            etc
            Moving to next pair is dictated by which coin is acquired. It could be pair_b or pair_c depending which
            pair has the acquired token
        """

        """ FORWARD """
        # SCENARIO I: Check if a_quote (acquired_coin) matches b_quote e.g. USDT_BTC | ETH_BTC
        if direction == 'forward':
            if a_quote == b_quote and calculated is False:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'quote_to_base'
                # Second leg of the trade
                contract_2 = pair_b

                # If b_base (acquired_coin) matches c_base e.g. USDT_BTC | ETH_BTC | ETH_USDT
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_c

                # If b_base (acquired_coin) matches c_quote e.g. USDT_BTC | BTC_ETH | USDT_ETH
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        # SCENARIO II: Check if a_quote (acquired_coin) matches b_base e.g. USDT_BTC | BTC_ETH
        if direction == 'forward':
            if a_quote == b_base and calculated is False:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'base_to_quote'
                # Second leg of the trade
                contract_2 = pair_b

                # If b_quote (acquired_coin) matches c_base e.g. USDT_BTC | BTC_ETH | ETH_USDT
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_c

                # If b_quote (acquired_coin) matches c_quote e.g. USDT_BTC | BTC_ETH | USDT_ETH
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        # SCENARIO III: Check if a_quote (acquired_coin) matches c_quote
        if direction == 'forward':
            if a_quote == c_quote and calculated is False:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'quote_to_base'
                # Second leg of the trade
                contract_2 = pair_c

                # If c_base (acquired_coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_b

                # If c_base (acquired_coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        # SCENARIO IV: Check if a_quote (acquired_coin) matches c_base
        if direction == 'forward':
            if a_quote == c_base and calculated is False:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'base_to_quote'
                # Second leg of the trade
                contract_2 = pair_c

                # If c_quote (acquired_coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_b

                # If c_quote (acquired_coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        """ REVERSE """
        # SCENARIO I: Check if a_base (acquired_coin) matches b_quote e.g. USDT_BTC | ETH_USDT
        if direction == 'reverse':
            if a_base == b_quote and calculated is False:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'quote_to_base'
                # Second leg of the trade
                contract_2 = pair_b

                # If b_base (acquired_coin) matches c_base e.g. USDT_BTC | ETH_USDT | ETH_BTC
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_c

                # If b_base (acquired_coin) matches c_quote e.g. USDT_BTC | ETH_USDT | ETH_BTC
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        # SCENARIO II: Check if a_base (acquired_coin) matches b_base e.g. USDT_BTC | USDT_ETH
        if direction == 'reverse':
            if a_base == b_base and calculated is False:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'base_to_quote'
                # Second leg of the trade
                contract_2 = pair_b

                # If b_quote (acquired_coin) matches c_base e.g. USDT_BTC | BTC_ETH | ETH_USDT
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_c

                # If b_quote (acquired_coin) matches c_quote e.g. USDT_BTC | BTC_ETH | USDT_ETH
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        # SCENARIO III: Check if a_base (acquired_coin) matches c_quote
        if direction == 'reverse':
            if a_base == c_quote and calculated is False:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'quote_to_base'
                # Second leg of the trade
                contract_2 = pair_c

                # If c_base (acquired_coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_b

                # If c_base (acquired_coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        # SCENARIO IV: Check if a_base (acquired_coin) matches c_base
        if direction == 'reverse':
            if a_base == c_base and calculated is False:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = 'base_to_quote'
                # Second leg of the trade
                contract_2 = pair_c

                # If c_quote (acquired_coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = 'base_to_quote'
                    # Third leg of the trade
                    contract_3 = pair_b

                # If c_quote (acquired_coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = 'quote_to_base'
                    # Third leg of the trade
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                # Trades finished for a group
                calculated = True

        """ PROFIT LOSS OUTPUT """
        # Profile and Loss calculation
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_percent = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

        # Trade descriptions
        trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} " \
                              f"acquiring {acquired_coin_t1}."
        trade_description_2 = f"Swap {acquired_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring " \
                              f"{acquired_coin_t2}."
        trade_description_3 = f"Swap {acquired_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring " \
                              f"{acquired_coin_t3}."

        # Output results
        if profit_loss_percent > min_surface_rate:
            surface_dictionary = {
                'swap_1': swap_1,
                'swap_2': swap_2,
                'swap_3': swap_3,
                'contract_1': contract_1,
                'contract_2': contract_2,
                'contract_3': contract_3,
                'direction_trade_1': direction_trade_1,
                'direction_trade_2': direction_trade_2,
                'direction_trade_3': direction_trade_3,
                'starting_amount': starting_amount,
                'acquired_coin_t1': acquired_coin_t1,
                'acquired_coin_t2': acquired_coin_t2,
                'acquired_coin_t3': acquired_coin_t3,
                'swap_1_rate': swap_1_rate,
                'swap_2_rate': swap_2_rate,
                'swap_3_rate': swap_3_rate,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'direction': direction,
                'trade_description_1': trade_description_1,
                'trade_description_2': trade_description_2,
                'trade_description_3': trade_description_3
            }
            return surface_dictionary

    return surface_dictionary
