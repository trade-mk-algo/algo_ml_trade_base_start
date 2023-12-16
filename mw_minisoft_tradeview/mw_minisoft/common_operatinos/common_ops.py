import pandas as pd

from mw_minisoft.constants.file_constants import FIREFOX_DRIVER_PATH
from mw_minisoft.persistence_operations.account_management import read_user_info
from mw_minisoft.session_builder.retrive_request_token import create_user_session


def super_user_session():
    user_info_df = read_user_info()
    user_info_df = user_info_df.loc[user_info_df['zerodha_datafeed'] == 'Y']
    sp_user_session, sp_user_record = create_user_session(user_info_df.loc[0], FIREFOX_DRIVER_PATH)
    return sp_user_session, sp_user_record


def multi_order_qty_normal_order(ind_record, tradeview_data_json):
    ticks_indicator = pd.read_csv("resources/telegram/day_instrument_orders.csv")
    ticks_indicator = ticks_indicator[ticks_indicator['instrument name'] == ind_record.instrument_name]
    ticks_indicator = ticks_indicator[ticks_indicator['strategy_name'] == ind_record.start_name]
    multi_order_qty_ = ind_record.default_quantity
    if ind_record.multi_quan == 'Y':
        for user_order_position, user_order in ticks_indicator.iterrows():
            if user_order['instrument profit or loss'] < 0:
                multi_order_qty_ = multi_order_qty_ + ind_record.default_quantity
            elif user_order['instrument profit or loss'] > 0:
                multi_order_qty_ = ind_record.default_quantity

    if tradeview_data_json['expiry_day'] == 'Y':
        multi_order_qty_ = ticks_indicator.iloc[-1]['instrument entry qty']

    return multi_order_qty_


def multi_order_qty_normal_instagram(ind_record, tradeview_data_json):
    ticks_indicator = pd.read_csv("resources/telegram/day_instrument_orders.csv")
    ticks_indicator = ticks_indicator[ticks_indicator['instrument name'] == ind_record.instrument_name]
    ticks_indicator = ticks_indicator[ticks_indicator['strategy_name'] == ind_record.start_name]
    multi_order_qty_ = ind_record.default_quantity
    if ind_record.multi_quan == 'Y':
        for user_order_position, user_order in ticks_indicator.iterrows():
            if user_order['instrument profit or loss'] < 0:
                multi_order_qty_ = multi_order_qty_ + ind_record.default_quantity
            elif user_order['instrument profit or loss'] > 0:
                multi_order_qty_ = ind_record.default_quantity

    multi_order_qty_ = multi_order_qty_ * ind_record.telegram_qty

    if tradeview_data_json['expiry_day'] == 'Y':
        multi_order_qty_ = ticks_indicator.iloc[-1]['instrument entry qty']
    return multi_order_qty_


def multi_order_qty_normal_original(ind_record, user_id, tradeview_data_json):
    ticks_indicator = pd.read_csv("resources/telegram/day_instrument_orders.csv")
    ticks_indicator = ticks_indicator[ticks_indicator['instrument name'] == ind_record.instrument_name]
    ticks_indicator = ticks_indicator[ticks_indicator['strategy_name'] == ind_record.start_name]
    multi_order_qty_ = ind_record.default_quantity
    if ind_record.multi_quan == 'Y':
        for user_order_position, user_order in ticks_indicator.iterrows():
            if user_order['instrument profit or loss'] < 0:
                multi_order_qty_ = multi_order_qty_ + ind_record.default_quantity
            elif user_order['instrument profit or loss'] > 0:
                multi_order_qty_ = ind_record.default_quantity

    if tradeview_data_json['expiry_day'] == 'Y':
        multi_order_qty_ = ticks_indicator.iloc[-1]['instrument entry qty']
    print('----------------------------------------------------')
    print(multi_order_qty_)
    print(ind_record[user_id])
    return multi_order_qty_ * ind_record[user_id]

