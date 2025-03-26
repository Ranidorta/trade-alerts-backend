import talib
import pandas as pd
from dataclasses import dataclass
from typing import List

@dataclass
class TradingSignal:
    symbol: str
    timestamp: pd.Timestamp
    signal: str  # Enum recomendado
    confidence: float

class SignalGenerator:
    def __init__(self, symbol: str):
        self.symbol = symbol
        
    def run(self) -> List[TradingSignal]:
        """Orquestra geração de sinais"""
        df = self._get_market_data()
        return [
            *self._generate_rsi_signals(df),
            *self._generate_macd_signals(df)
        ]
    
    def _get_market_data(self) -> pd.DataFrame:
        """Obter dados tratados"""
        pass
