ffrom flask import Flask, jsonify
import pandas as pd
import pandas_ta as ta
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Seu código existente para webhook aqui...
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Exporta o app para ser importado pelo app.py
if __name__ == '__main__':
    app.run(debug=True)
