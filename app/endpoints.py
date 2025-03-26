from flask import Blueprint, jsonify
from core.engine import TradingEngine
from .schemas import SignalSchema

bp = Blueprint('api', __name__)
engine = TradingEngine()

@bp.route('/signals', methods=['GET'])
def get_signals():
    signals = engine.generate_signals(["BTCUSDT", "ETHUSDT"])
    return jsonify(SignalSchema().dump(signals, many=True))
