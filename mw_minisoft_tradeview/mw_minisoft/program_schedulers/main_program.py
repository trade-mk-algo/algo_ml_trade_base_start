import json
import os
import sys

from mw_minisoft.instruments_operations.instrument_read_write_operations import download_write_instrument_tokens
from mw_minisoft.order_management.generate_strategy_orders import storage_regular_orders
from mw_minisoft.persistence_operations.account_management import *
from datetime import timedelta
from mw_minisoft.session_builder.retrive_request_token import generate_user_session


def check_inst_expiry_date():
    inst_split_columns = ['script', 'year', 'mon', 'day', 'strike_price', 'option_type_1']
    instruments = pd.read_csv(INSTRUMENTS_DATA_FILE, low_memory=False)
    day_inst_orders = pd.read_csv(DAY_INSTRUMENT_ORDERS, low_memory=False)
    day_inst_orders = day_inst_orders[day_inst_orders['instrument exit type'].isna()]
    day_inst_orders_days = pd.to_datetime(day_inst_orders['instrument date'])
    current_day = pd.to_datetime(datetime.now().date())
    market_running = (day_inst_orders_days[day_inst_orders_days > current_day]).shape[0]
    for day_inst_index, day_inst_order in day_inst_orders.iterrows():
        inst_filter = instruments[instruments['Expiry date'] == day_inst_order['instrument entry type']]
        inst_filter[inst_split_columns] = inst_filter['Symbol Details'].str.split(' ', expand=True)
        inst_dates = pd.to_datetime((inst_filter['year'] + inst_filter['mon'] + inst_filter['day']), format='%y%b%d')
        instrument_days = inst_dates.dt.date
        instrument_days = instrument_days.iloc[-1]
        cond = date.today() + timedelta(days=2) >= instrument_days
        if cond:
            instrument_name = day_inst_order["instrument name"]
            start_name = day_inst_order["strategy_name"]
            if 'CE' in day_inst_order["instrument entry type"][-2:]:
                entry_type = 'buy'
            elif 'PE' in day_inst_order["instrument entry type"][-2:]:
                entry_type = 'sell'
            tradeview_data = {
                "instrument_name": instrument_name,
                "start_name": start_name,
                "entry_type": entry_type,
                "expiry_day": "Y"
            }
            strategy_execution_steps(tradeview_data)

def user_account_balance():
    user_amount = pd.DataFrame()
    user_accounts = pd.read_csv(USER_INPUTS_FILE)
    for user_account_index, user_account in user_accounts.iterrows():
        user_session = generate_user_session(user_account)
        user_data = pd.DataFrame(user_session.funds()['fund_limit'])
        user_data_balance = user_data[user_data['title'] == 'Total Balance']
        user_data_df = {'date': str(date.today()), 'user_name': user_account['name'],
                        'user_id': user_account.user_id,
                        'balance': "{:,}".format(int(user_data_balance.equityAmount.values[0]))}
        user_amount = user_amount.append(user_data_df, ignore_index=True)
    user_amount.to_csv('resources/telegram/user_amount.csv', index=False)
    print(user_amount)
    return user_amount	

def strategy_execution_steps(tradeview_data):
    """
    New instrument data will be added, and technical values will be generated on top of it; recently,
    the order management process will begin.
    """
    # user_account_balance()
    # some JSON:
    # tradeview_data = '{"instrument_name":"NSE:USDINR", "start_name":"sp_dir_7_3_5min", "entry_type":"buy", "expiry_day":"N"}'
    #tradeview_data_json = json.loads(tradeview_data)
    storage_regular_orders(tradeview_data)
    # place_regular_orders(auto_inputs)
    # write_user_positions()


def remove_create_dir():
    """
    All files such as order, user order, and ticks will be deleted.
    """
    # folders = [ORDERS_FOLDER_, TICKS_FOLDER_, USER_ORDERS_FOLDER_, USER_ORDERS_POSITIONS_]
    folders = [TICKS_FOLDER_, USER_ORDERS_POSITIONS_]
    cus_logger.info('The process of deleting old files has begun.')
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            os.remove(file_path)


def execute_strategy_programs():
    """
    A user session token will be generated, and the most recent instruments file will be downloaded and saved to the
    local directory.
    """
    cus_logger.info("strategy execution started")
    user_info = pd.read_csv(USER_INPUTS_FILE)
    user_info = user_info[user_info.day != date.today().day]
    if user_info.shape[0] > 0:
        download_each_user_tokens()
        update_ticks_info()
        download_write_instrument_tokens()
        remove_create_dir()

    cus_logger.info("strategy execution completed")


def scheduler_main_program_run(tradeview_data):
    """
    This function will update the input parameters and launch the main programme.
    """
    try:
        cus_logger.info("%s main program execution started")
        strategy_execution_steps(tradeview_data)
        cus_logger.info("%s main program execution ended")
    except Exception as exception:
        cus_logger.exception(exception)
