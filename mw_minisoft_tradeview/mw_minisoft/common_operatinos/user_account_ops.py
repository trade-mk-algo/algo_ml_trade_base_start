from mw_minisoft.order_management.order_management__ce_pe import *
from mw_minisoft.persistence_operations.account_management import *


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