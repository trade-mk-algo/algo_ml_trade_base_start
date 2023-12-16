from strategy_builder.strategy_super_long import strategy_super_long_data_builder
from strategy_builder.strategy_super_short import strategy_super_short_data_builder
from strategy_builder.strategy_super_short_open import day_open_str_data_builder
from strategy_builder.super_long_buy_side import super_long_buy_side_results
from strategy_builder.super_long_sell_side import super_long_sell_side_results
import pandas as pd


def strategy_data_builder_(instrument_history_data, auto_inputs, instrument_name):
    day_open_str = day_open_str_data_builder(instrument_history_data, auto_inputs, instrument_name)
    super_long_buy_side = super_long_buy_side_results(instrument_history_data, auto_inputs, instrument_name)
    super_long_buy_side_merge = pd.merge_asof(day_open_str, super_long_buy_side, on="date")
    super_long_sell_side = super_long_sell_side_results(instrument_history_data, auto_inputs, instrument_name)
    super_long_sell_side_merge = pd.merge_asof(super_long_buy_side_merge, super_long_sell_side, on="date")
    # strategy_super_short = strategy_super_short_data_builder(instrument_history_data, auto_inputs, instrument_name)
    # merged_dataframe = pd.merge_asof(day_open_str, strategy_super_short, on="date")
    # strategy_super_long = strategy_super_long_data_builder(instrument_history_data, auto_inputs, instrument_name)
    return super_long_sell_side_merge
