from tenacity import retry, stop_after_attempt
import requests
import pandas as pd

class BybitService:
    def __init__(self, api_key: str, api_secret: str):
        self.base_url = "https://api.bybit.com/v5"
        self.session = requests.Session()
        
    @retry(stop=stop_after_attempt(3))
    def get_klines(self, symbol: str, interval: str) -> pd.DataFrame:
        """Obtém dados com tratamento de erro e retry automático"""
        response = self.session.get(
            f"{self.base_url}/market/kline",
            params={"symbol": symbol, "interval": interval}
        )
        response.raise_for_status()
        return self._parse_response(response.json())
    
    def _parse_response(self, data: dict) -> pd.DataFrame:
        """Transformação segura dos dados"""
        df = pd.DataFrame(data['result']['list'])
        df['close'] = df['close'].astype(float)
        return df
