from flask import Flask

app = Flask(__name__)

# ... suas rotas e configurações ...

# No final do arquivo
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
