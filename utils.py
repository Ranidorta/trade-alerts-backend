import requests
import pandas as pd
import numpy as np
from database import save_signal
from datetime import datetime

BYBIT_API_URL = "https://api.bybit.com/v5/market/kline"
INTERVAL = "1h"
CANDLE_LIMIT = 200
RISK_REWARD_RATIO = 1.5
RISK_PER_TRADE = 0.02
ACCOUNT_BALANCE = 10000

# ===== Indicadores base (sem talib) =====
def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def sma(series, period=14):
    return series.rolling(window=period).mean()

def atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def adx(df, period=14):
    up_move = df['high'].diff()
    down_move = df['low'].diff().abs()

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    tr = df[['high', 'low', 'close']].copy()
    tr['tr'] = df['high'].combine(df['close'].shift(), max) - df['low'].combine(df['close'].shift(), min)
    tr = tr['tr'].rolling(period).mean()

    plus_di = 100 * (pd.Series(plus_dm).rolling(period).sum() / tr)
    minus_di = 100 * (pd.Series(minus_dm).rolling(period).sum() / tr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    return dx.rolling(period).mean()

# ===== Estratégias de Sinal =====
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

# ===== Coleta e Extração =====
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
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
        return df
    return pd.DataFrame()

def extract_features(df):
    df['rsi'] = rsi(df['close'])
    df['ma_short'] = sma(df['close'], 5)
    df['ma_long'] = sma(df['close'], 20)
    df['atr'] = atr(df, 14)
    df['macd'], df['macd_signal'] = macd(df['close'])
    df['ma_fast'] = sma(df['close'], 9)
    df['ma_slow'] = sma(df['close'], 21)
    df['adx'] = adx(df)
    df['high_prev'] = df['high'].shift(1)
    df['low_prev'] = df['low'].shift(1)
    df['atr_mean'] = df['atr'].rolling(14).mean()
    return df.dropna()

# ===== Simulação e Cálculo =====
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

