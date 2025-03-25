import pandas as pd
import numpy as np
import requests

# =====================
# CONFIGURAÇÕES
# =====================
BYBIT_API_URL = "https://api.bybit.com/v5/market/kline"
INTERVAL = "1h"
CANDLE_LIMIT = 100

# =====================
# OBTÉM TODOS OS ATIVOS DE FUTUROS USDT
# =====================
def get_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {"category": "linear"}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        if "result" in data and "list" in data["result"]:
            return [s["symbol"] for s in data["result"]["list"] if "USDT" in s["symbol"]]
        else:
            return []
    except Exception as e:
        print("Erro ao buscar símbolos:", e)
        return []

# =====================
# OBTÉM OS CANDLESTICKS PARA UM ATIVO
# =====================
def get_candles(symbol):
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": CANDLE_LIMIT
    }
    try:
        res = requests.get(BYBIT_API_URL, params=params)
        data = res.json()
        if "result" in data and "list" in data["result"]:
            candles = data["result"]["list"]
            df = pd.DataFrame(candles, columns=[
                "timestamp", "open", "high", "low", "close", "volume", "turnover"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
            return df
    except Exception as e:
        print(f"Erro ao buscar candles para {symbol}:", e)
    return pd.DataFrame()

# =====================
# PROCESSA UM ATIVO E GERA SINAL SIMPLES
# =====================
def process_symbol(symbol):
    df = get_candles(symbol)
    if df.empty:
        print(f"[!] Sem dados para {symbol}")
        return None

    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["signal"] = np.where(df["ma5"] > df["ma20"], "BUY", "SELL")
    return df[["timestamp", "close", "ma5", "ma20", "signal"]]
