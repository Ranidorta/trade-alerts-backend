import requests
import pandas as pd
import numpy as np
import talib
from database import save_signal
from datetime import datetime

BYBIT_API_URL = "https://api.bybit.com/v5/market/kline"
INTERVAL = "1h"
CANDLE_LIMIT = 200
RISK_REWARD_RATIO = 1.5
RISK_PER_TRADE = 0.02
ACCOUNT_BALANCE = 10000

# ========== Estratégias ==========
def strategy_classic(row):
    if row['rsi'] < 30 and row['ma_short'] > row['ma_long'] and row['macd'] > row['macd_signal']:
        return 1
    elif row['rsi'] > 70 and row['ma_short'] < row['ma_long'] and row['macd'] < row['macd_signal']:
        return -1
    return 0

def strategy_fast(row):
    if row['rsi'] < 40 and row['macd'] > row['macd_signal']:
        return 1
    elif row['rsi'] > 60 and row['macd'] < row['macd_signal']:
        return -1
    return 0

def strategy_rsi_macd(row):
    if row['rsi'] < 30 and row['macd'] > row['macd_signal']:
        return 1
    elif row['rsi'] > 70 and row['macd'] < row['macd_signal']:
        return -1
    return 0

def strategy_breakout_atr(row):
    if row['atr'] > row['atr_mean']:
        if row['close'] > row['high_prev']:
            return 1
        elif row['close'] < row['low_prev']:
            return -1
    return 0

def strategy_trend_adx(row):
    if row['adx'] > 20:
        if row['ma_fast'] > row['ma_slow']:
            return 1
        elif row['ma_fast'] < row['ma_slow']:
            return -1
    return 0

# ========== Coleta ==========
def get_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {"category": "linear"}
    response = requests.get(url, params=params)
    data = response.json()
    return [s["symbol"] for s in data["result"]["list"] if s["symbol"].endswith("USDT")]

def get_candles(symbol, interval="1h", limit=200):
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    res = requests.get(BYBIT_API_URL, params=params)
    data = res.json()
    if "result" in data and "list" in data["result"]:
        candles = data["result"]["list"]
        df = pd.DataFrame(candles, columns=[
            "timestamp", "open", "high", "low", "close", "volume", "turnover"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
        return df
    return pd.DataFrame()

# ========== Indicadores ==========
def extract_features(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['ma_short'] = talib.SMA(df['close'], timeperiod=5)
    df['ma_long'] = talib.SMA(df['close'], timeperiod=20)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], 12, 26, 9)
    df['ma_fast'] = talib.SMA(df['close'], timeperiod=9)
    df['ma_slow'] = talib.SMA(df['close'], timeperiod=21)
    df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['high_prev'] = df['high'].shift(1)
    df['low_prev'] = df['low'].shift(1)
    df['atr_mean'] = df['atr'].rolling(14).mean()
    return df.dropna()

# ========== Lógica ==========
def calculate_position_size(capital, atr, risk_pct):
    risk = capital * risk_pct
    return round(risk / atr, 2) if atr > 0 else 0

def calculate_leverage(atr):
    if atr > 10:
        return 3
    elif atr > 5:
        return 5
    else:
        return 10

def simulate_trade(row):
    atr = row['atr']
    entry = row['close']
    tp = entry + (atr * RISK_REWARD_RATIO) if row['signal'] == 1 else entry - (atr * RISK_REWARD_RATIO)
    sl = entry - atr if row['signal'] == 1 else entry + atr
    future = row['close']
    if row['signal'] == 1 and future >= tp:
        return 1
    elif row['signal'] == -1 and future <= tp:
        return 1
    elif row['signal'] == 1 and future <= sl:
        return 0
    elif row['signal'] == -1 and future >= sl:
        return 0
    return None

# ========== Execução ==========
def process_symbol(symbol):
    df = get_candles(symbol, interval=INTERVAL, limit=CANDLE_LIMIT)
    if df.empty:
        print(f"Sem dados para: {symbol}")
        return
    df = extract_features(df)

    strategies = {
        "CLASSIC": strategy_classic,
        "FAST": strategy_fast,
        "RSI_MACD": strategy_rsi_macd,
        "BREAKOUT_ATR": strategy_breakout_atr,
        "TREND_ADX": strategy_trend_adx,
    }

    for name, func in strategies.items():
        df['signal'] = df.apply(func, axis=1)
        df['result'] = df.apply(simulate_trade, axis=1)
        df['position_size'] = df.apply(lambda r: calculate_position_size(ACCOUNT_BALANCE, r['atr'], RISK_PER_TRADE), axis=1)
        df['leverage'] = df['atr'].apply(calculate_leverage)

        for _, row in df[df['signal'] != 0].dropna().iterrows():
            save_signal(
                symbol,
                name,
                row['signal'],
                row['result'],
                row['position_size'],
                row['close'],
                row['leverage']
            )
            print(f"[{name}] {symbol} sinal={row['signal']} resultado={row['result']} leve={row['leverage']}")
