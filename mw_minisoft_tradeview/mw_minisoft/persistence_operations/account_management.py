import datetime
from datetime import datetime, date

import pandas as pd
from trade_logger.logger import cus_logger

from mw_minisoft.constants.file_constants import *
from mw_minisoft.session_builder.retrive_request_token import create_user_session

cus_logger.setLevel(10)


def read_user_info():
    """
    All user info will read and send as data-frame
    """
    cus_logger.info("stated read user info data from user_info file")
    user_info_excel = pd.read_csv(USER_INPUTS_FILE)
    return pd.DataFrame(user_info_excel).astype(str)


def write_user_info(user_id, request_token, public_token, access_token):
    """
    generated user session tokens will be stored
    """
    cus_logger.info("storing user token information in the file sys")
    user_records = pd.read_csv(USER_INPUTS_FILE)
    user_records_data = pd.DataFrame(user_records).astype(str)
    for user_record_position, user_info_record in user_records_data.iterrows():
        if user_info_record['user_id'] == user_id:
            user_records_data.at[user_record_position, 'request_token'] = request_token
            user_records_data.at[user_record_position, 'day'] = date.today().day
            user_records_data.at[user_record_position, 'access_token'] = access_token
    user_records_data['login_pin'].astype(str)
    user_records_data.to_csv(USER_INPUTS_FILE, index=False)
    return user_records_data


def update_auto_inputs(env, minutes, super_trend_period, super_trend_multiplier):
    """
    user input data would be updated on auto_input csv file
   """
    cus_logger.info("updating the user input data into the auto_input.csv file")
    auto_inputs = pd.read_csv(AUTO_INPUTS_FILE)
    auto_inputs = pd.DataFrame(auto_inputs).astype(str)
    auto_inputs.at[0, 'scheduler_minutes'] = 1 * minutes
    auto_inputs.at[0, 'data_interval'] = str(1 * minutes)
    auto_inputs.at[0, 'super_trend_period'] = super_trend_period
    auto_inputs.at[0, 'super_trend_multiplier'] = super_trend_multiplier
    auto_inputs.at[0, 'env'] = env
    auto_inputs.to_csv(AUTO_INPUTS_FILE, index=False)


def download_each_user_tokens():
    """
    This code will be used to obtain the accessToken from the source system, which will then be used to access the
    order API and other services.
    """
    user_info = pd.read_csv(USER_INPUTS_FILE)
    user_info = user_info[user_info.day != date.today().day]
    for user_record_position, user_record in user_info.iterrows():
        cus_logger.info("user(%s) session token generation started", user_record.user_id)
        user_kite_session, user_record = create_user_session(user_record, FIREFOX_DRIVER_PATH)
        write_user_info(user_record.user_id, user_record.request_token, user_record.public_token,
                        user_record.access_token)
    cus_logger.info("session token generation completed ")


def ticks_indi():
    """
    instruments data will read and send as dataframe
   """
    cus_logger.info("instruments are reading from ticks_ind.csv file")
    ticks_ind_excel = pd.read_csv(TICKS_IND_FILE)
    return pd.DataFrame(ticks_ind_excel)


def update_ticks_info():
    ticks_info = pd.read_csv('resources/account/ticks_indi.csv')

    for ticks_info_position, ticks_info_record in ticks_info.iterrows():
        if ticks_info_record.update_required == 'Y':
            instruments = pd.read_csv(INSTRUMENTS_DATA_FILE, low_memory=False)
            instruments = instruments[(instruments['Scrip code'] == ticks_info_record.instrument_name.split(':')[1])
                                      & (instruments['Option type'] == 'XX') & (instruments['Minimum lot size'] != 0)]
            instruments[['script', 'year', 'mon', 'day', 'strike_price']] = instruments['Symbol Details'].str.split(' ',
                                                                                                                    expand=True)
            instrument_days = (pd.to_datetime((instruments['year'] + instruments['mon'] + instruments['day']),
                                              format='%y%b%d')).dt.date
            expiry_day = (instrument_days[instrument_days > datetime.now().date()]).head(1)
            expiry_day_record = instruments.loc[expiry_day.index.values[0]]
            expir_day = ((pd.to_datetime(
                (expiry_day_record['year'] + expiry_day_record['mon'] + expiry_day_record['day']),
                format='%y%b%d')).date())
            ticks_info.loc[ticks_info_position, 'instrument_token'] = expiry_day_record['Expiry date']
            ticks_info.loc[ticks_info_position, 'instrument_expiry_date'] = expir_day.strftime("%d-%m-%Y")
            ticks_info.loc[ticks_info_position, 'instrument_trading_symbol'] = expiry_day_record['Expiry date']
    ticks_info.to_csv(TICKS_IND_FILE, index=False)


def collect_user_id(kite_session):
    user_info = read_user_info()
    return (user_info[user_info.api_key == kite_session.client_id]).user_id.values[0]


def ticks_ind_collect_instrument(instrument_trading_symbol):
    ticks_ind = pd.read_csv(TICKS_IND_FILE)
    ticks_ind = ticks_ind[ticks_ind.instrument_trading_symbol == instrument_trading_symbol]
    return ticks_ind


def entry_time_l(instrument_name):
    entry_time_ = '09:00:00'
    if ('NSE' in instrument_name) and ('NIFTY' in instrument_name):
        entry_time_ = '09:15:00'
    elif ('NSE' in instrument_name) and ('INR' in instrument_name):
        entry_time_ = '09:00:00'
    elif 'MCX' in instrument_name:
        entry_time_ = '09:00:00'
    return entry_time_


def exit_time_l(instrument_name):
    exit_time_ = '15:30:00'
    if ('NSE' in instrument_name) and ('NIFTY' in instrument_name):
        exit_time_ = '15:29:00'
    elif ('NSE' in instrument_name) and ('INR' in instrument_name):
        exit_time_ = '16:58:00'
    elif 'MCX' in instrument_name:
        exit_time_ = '23:58:00'
    return exit_time_


def market_status(ticks):
    status = False
    auto_inputs = pd.read_csv(AUTO_INPUTS_FILE)
    auto_inputs = pd.DataFrame(auto_inputs).astype(str)
    exit_time_ = exit_time_l(ticks)
    entry_time_ = entry_time_l(ticks)
    current_time = datetime.now().time().strftime('%H:%M:%S')
    before_mkt = current_time < exit_time_
    after_mkt = current_time > entry_time_
    if auto_inputs.iloc[0].env == 'test':
        status = True
    elif 'NSE' in ticks and 'NIFTY' in ticks and before_mkt and after_mkt:
        status = True
    elif 'NSE' in ticks and 'INR' in ticks and before_mkt and after_mkt:
        status = True
    elif 'MCX' in ticks and before_mkt and after_mkt:
        status = True
    return status
