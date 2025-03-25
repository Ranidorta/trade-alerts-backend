import pandas as pd

def extract_features(df):
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma_diff'] = df['ma5'] - df['ma20']
    df.dropna(inplace=True)
    return df
