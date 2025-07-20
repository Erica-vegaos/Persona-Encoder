# Dockerfile // v1.0.1
FROM python:3.10-slim

# 安裝必要依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libatlas-base-dev libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
