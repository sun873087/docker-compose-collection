#!/bin/bash

# 設定腳本在遇到錯誤時立即退出
set -e

echo "🚀 啟動 Keycloak API 測試後端..."

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 找不到 Python3，請先安裝 Python"
    exit 1
fi

# 檢查是否在虛擬環境中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 使用虛擬環境: $VIRTUAL_ENV"
else
    echo "⚠️  警告: 建議在虛擬環境中執行"
    echo "   可以使用以下命令建立虛擬環境:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
fi

# 安裝依賴套件
echo "📦 使用 uv 安裝依賴套件..."
uv sync

# 啟動服務
echo "🌟 啟動 FastAPI 伺服器..."
echo "   後端 API 將運行在: http://localhost:8000"
echo "   API 文檔位於: http://localhost:8000/docs"
echo "   按 Ctrl+C 停止服務"
echo ""

uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload