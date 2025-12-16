FROM python:3.9-slim

# 安裝 mkcert 依賴 (libnss3-tools) 和 wget
RUN apt-get update && apt-get install -y \
    libnss3-tools \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 下載 mkcert (Linux AMD64 版本)
RUN wget -O /usr/local/bin/mkcert "https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64" \
    && chmod +x /usr/local/bin/mkcert

# 設定工作目錄
WORKDIR /app

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 暴露端口
EXPOSE 7777

CMD ["python", "app.py"]