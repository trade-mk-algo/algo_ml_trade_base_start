import sys

from trade_logger.logger import cus_logger

from mw_minisoft.manual_exit.main_program_manual_exit import user_positions, user_positions_write


def scheduler_main_program_run():
    """
    This function will update the input parameters and launch the main programme.
    """
    try:
        #user_positions("NSE:NIFTY2361518750CE")
        user_positions_write()
        cus_logger.info("%s main program execution ended")
        sys.exit()
    except Exception as exception:
        cus_logger.exception(exception)


scheduler_main_program_run()