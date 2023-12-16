import time

from flask import Flask, request, abort

from mw_minisoft.manual_exit.main_program_manual_exit import strategy_manual_exit
from mw_minisoft.program_schedulers.main_program import *
from waitress import serve
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        scheduler_main_program_run(request.json)
        print(request.json)
        request.close()
        return 'success', 200
    else:
        abort(400)


@app.route('/expiry', methods=['POST'])
def expiry():
    if request.method == 'POST':
        check_inst_expiry_date()
        print(request.json)
        request.close()
        return 'success', 200
    else:
        abort(400)

@app.route('/user_bal', methods=['GET'])
def user_bal():
    if request.method == 'GET':
        user_amount = user_account_balance()
        request.close()
        return user_amount.to_json(), 200
    else:
        abort(400)

@app.route('/token_gen', methods=['POST'])
def token_gen():
    if request.method == 'POST':
        execute_strategy_programs()
        request.close()
        return 'success', 200
    else:
        abort(400)

@app.route('/manual_exit', methods=['POST'])
def manual_exit():
    if request.method == 'POST':
        strategy_manual_exit(request.json)
        request.close()
        return 'success', 200
    else:
        abort(400)

serve(app, host="0.0.0.0", port=80 )

