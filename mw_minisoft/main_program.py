from mw_minisoft.program_schedulers.main_program import *

scheduler_main_program_run('prod', 1, 7, 3)
#user_account_balance()


# TODO
# Check conversion is working as is expected or nor
# incase 5 min order is triggered -> before the 5 min candle complete -> which means conversion is not working ->
# ->  Advantage -> order will be placed immediate signal generation -> if need order to be placed -> after conformation
# -> work on the time services conversion


