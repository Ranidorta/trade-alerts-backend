import requests
from tenacity import retry, stop_after_attempt
import pandas as pd

class BybitClient:
    BASE_URL = "https://api.bybit.com/v5"

    @retry(stop=stop_after_attempt(3))
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
        response = requests.get(
            f"{self.BASE_URL}/market/kline",
            params={
                "category": "linear",
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
        )
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['result']['list'])
        df = df.astype({
            "open": float, "high": float, "low": float, 
            "close": float, "volume": float
        })
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.attrs['symbol'] = symbol
        return df
