# 使用官方 Python 3.9 映像作為基礎
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝 Python 套件
# 先複製 requirements.txt 可以利用 Docker 快取機制
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 procps 套件（提供 ps 指令）
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

# 複製應用程式代碼
COPY . .

# 建立非 root 使用者（安全最佳實踐）
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 聲明應用程式端口
EXPOSE 5000

# 設定環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 設定容器啟動指令
CMD ["python", "app.py"]