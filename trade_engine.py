from utils import get_symbols, process_symbol
from database import save_signal
from indicators import extract_features

def generate_all_signals():
    symbols = get_symbols()
    for symbol in symbols:
        process_symbol(symbol)
