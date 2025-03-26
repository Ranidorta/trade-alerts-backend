from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from services.bybit_client import BybitClient
from .indicators import FeatureEngine
from .exceptions import SignalGenerationError
from utils.logger import get_logger

logger = get_logger(__name__)

class TradingEngine:
    def __init__(self, max_workers=5):
        self.client = BybitClient()
        self.feature_engine = FeatureEngine()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def process_symbol(self, symbol: str) -> List[Dict]:
        try:
            df = self.client.get_klines(symbol)
            signals = self.feature_engine.generate_all_signals(df)
            return [s.to_dict() for s in signals]
        except Exception as e:
            logger.error(f"Signal generation failed for {symbol}", exc_info=True)
            raise SignalGenerationError(symbol)

    def generate_signals(self, symbols: List[str]) -> Dict[str, List[Dict]]:
        results = {}
        futures = {
            self.executor.submit(self.process_symbol, symbol): symbol
            for symbol in symbols
        }
        for future in futures:
            symbol = futures[future]
            results[symbol] = future.result()
        return results
