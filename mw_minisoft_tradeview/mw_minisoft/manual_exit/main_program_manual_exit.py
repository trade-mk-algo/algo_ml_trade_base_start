import os
import sys

from mw_minisoft.constants.file_constants import *
from mw_minisoft.order_management.order_management__ce_pe import *
from mw_minisoft.persistence_operations.account_management import *


def strategy_manual_exit(manual_exit_data):
    """
    New instrument data will be added, and technical values will be generated on top of it; recently,
    the order management process will begin.
    """
    # write_user_positions()

    user_records = pd.read_csv(USER_INPUTS_FILE)

    for user_record_position, user_record in user_records.iterrows():
        try:
            user_session = generate_user_session(user_record)
            trading_symbol = manual_exit_data['instrument_name']
            data = {"symbol": trading_symbol, "ohlcv_flag": "1"}
            price_last, order_info = 0, "order info not available"
            order_qty = manual_exit_data['order_quantity']
            market_type = 'MARGIN'
            try:
                price_last = (user_session.depth(data)['d'][trading_symbol]['ask'])[4]['price']
            except Exception as exception:
                cus_logger.error(str(exception))
            cus_logger.info('Exiting position :- instrument_token: %s ,User( %s) ,  Order Type : buy order , '
                            'ticks_ind_running_qt: %s , price: %s ', trading_symbol, user_record.user_id, order_qty,
                            price_last)
            data = {"symbol": trading_symbol, "qty": order_qty, "type": 1, "side": -1, "productType": market_type,
                    "limitPrice": price_last, "stopPrice": 0, "validity": "DAY", "disclosedQty": 0, "offlineOrder": "False",
                    "stopLoss": 0, "takeProfit": 0}
            try:
                order_info = user_session.place_order(data)
            except Exception as exception:
                cus_logger.error(str(exception))
            cus_logger.info('Instrument Order Detail, order info %s', str(order_info))
        except Exception as all_errors:
            cus_logger.error("User (%s) Entering into new order Instrument position (%s) had been failed - "
                             "error message %s", user_record.user_id, "inst_record.instrument_name", all_errors)
    order_info = "";
