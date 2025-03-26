FROM python:3.11-slim

# Instala dependências do sistema para TA-Lib
RUN apt-get update && \
    apt-get install -y build-essential && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    rm -rf ta-lib*

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "app:app"]
