from concurrent.futures import ThreadPoolExecutor
from typing import List
from core.engine import SignalGenerator

class SignalService:
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers)
        
    def generate_signals(self, symbols: List[str]) -> dict:
        """Processamento paralelo de sinais"""
        with self.executor:
            return {
                symbol: SignalGenerator(symbol).run()
                for symbol in symbols
            }
