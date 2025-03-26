from flask import Flask
from routes import app  # Importa o app já configurado do routes.py

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
