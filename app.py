from flask import Flask, request, jsonify
from trade_engine import generate_all_signals
from database import init_db, get_all_signals

app = Flask(__name__)
init_db()

@app.route('/signals', methods=['GET'])
def signals():
    strategy = request.args.get('strategy')
    symbol = request.args.get('symbol')
    user_id = request.args.get('user_id')
    data = get_all_signals(strategy=strategy, symbol=symbol, user_id=user_id)
    return jsonify(data)

@app.route('/run', methods=['POST'])
def run_engine():
    generate_all_signals()
    return jsonify({"message": "Sinais gerados com sucesso!"})

if __name__ == '__main__':
    app.run(debug=True)
