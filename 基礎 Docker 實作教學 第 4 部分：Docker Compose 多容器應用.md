# 基礎 Docker 實作教學(第四部分：Docker Compose 多容器應用)

課程時間：30 分鐘

- Docker Compose 基本概念與語法
- 實作練習：建立 Web + 資料庫應用

---

## Docker Compose 基本概念與語法

### ✨什麼是 Docker Compose？

在前面的課程中，我們學會了如何建立和運行單一容器。但在實際的應用場景中，大多數應用都需要多個服務協同工作，例如：
- Web 應用程式 + 資料庫
- 前端 + 後端 API + 資料庫
- 微服務架構中的多個服務

如果我們要手動管理多個容器，會遇到以下問題：
- 需要記住每個容器的啟動指令和參數
- 容器間的網路連接配置複雜
- 服務啟動順序難以控制
- 環境變數和配置管理困難

**Docker Compose** 就是為了解決這些問題而生的工具！它讓我們可以用一個簡單的 YAML 檔案來定義和管理多容器應用。

### 🏗️ 為什麼需要 Docker Compose？

#### 1. 簡化多容器管理
```bash
# 傳統方式：需要多個指令
docker network create myapp-network
docker run -d --name database --network myapp-network -e MYSQL_ROOT_PASSWORD=secret mysql:8.0
docker run -d --name webapp --network myapp-network -p 8080:5000 my-flask-app

# Docker Compose 方式：一個指令搞定
docker-compose up -d
```

#### 2. 環境一致性
- **開發環境**：開發人員可以快速啟動完整的應用環境
- **測試環境**：測試人員可以獲得與生產環境一致的配置
- **生產環境**：部署時確保所有服務配置正確

#### 3. 版本控制和協作
- `docker-compose.yml` 檔案可以納入版本控制
- 團隊成員可以共享相同的環境配置
- 環境變更可以透過 Git 追蹤和管理

### 📋 docker-compose.yml 檔案基本結構

Docker Compose 使用 YAML 格式的配置檔案，基本結構如下：

```yaml
version: '3.8'  # Compose 檔案格式版本

services:       # 定義所有服務
  web:          # 服務名稱
    # 服務配置
  database:     # 另一個服務
    # 服務配置

networks:       # 自定義網路（可選）
  # 網路配置

volumes:        # 持久化儲存（可選）
  # 卷配置
```

### 🔧 常用 Docker Compose 語法詳解

#### 1. services - 服務定義

```yaml
services:
  # 使用現有映像
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    
  # 從 Dockerfile 建立
  app:
    build: .                    # 使用當前目錄的 Dockerfile
    build:                      # 或者詳細配置
      context: ./app
      dockerfile: Dockerfile.dev
```

#### 2. ports - 端口映射

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"              # 主機端口:容器端口
      - "8443:443"
      - "127.0.0.1:9000:9000"  # 綁定特定 IP
```

#### 3. environment - 環境變數

```yaml
services:
  database:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: apppass
    # 或者使用環境檔案
    env_file:
      - .env
```

#### 4. volumes - 資料持久化

```yaml
services:
  database:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql           # 命名卷
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # 綁定掛載
      - /host/logs:/var/log              # 主機路徑掛載

volumes:
  db_data:    # 定義命名卷
```

#### 5. depends_on - 服務依賴

```yaml
services:
  web:
    image: my-web-app
    depends_on:
      - database
      - redis
    
  database:
    image: mysql:8.0
    
  redis:
    image: redis:alpine
```

#### 6. networks - 網路配置

```yaml
services:
  web:
    image: nginx
    networks:
      - frontend
      - backend
      
  database:
    image: mysql:8.0
    networks:
      - backend

networks:
  frontend:
  backend:
```

### 🚀 基本 Docker Compose 指令

#### 1. 啟動和停止服務

```bash
# 啟動所有服務（前台運行）
docker-compose up

# 啟動所有服務（背景運行）
docker-compose up -d

# 停止所有服務
docker-compose down

# 停止並刪除所有資源（包括卷）
docker-compose down -v
```

#### 2. 建立和管理

```bash
# 建立或重建服務
docker-compose build

# 建立並啟動
docker-compose up --build

# 只啟動特定服務
docker-compose up web database
```

#### 3. 監控和除錯

```bash
# 查看服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs
docker-compose logs web        # 特定服務的日誌
docker-compose logs -f web     # 即時跟蹤日誌

# 進入服務容器
docker-compose exec web bash
```

#### 4. 擴展和重啟

```bash
# 擴展服務實例
docker-compose up --scale web=3

# 重啟服務
docker-compose restart
docker-compose restart web    # 重啟特定服務
```

### 🎯 Docker Compose 最佳實踐

1. **使用環境檔案**：將敏感資訊放在 `.env` 檔案中
2. **合理命名服務**：使用有意義的服務名稱
3. **適當使用網路**：隔離不同層級的服務
4. **資料持久化**：重要資料使用命名卷儲存
5. **健康檢查**：為關鍵服務添加健康檢查

---

## 實作練習：建立 Web + 資料庫應用

在這個實作練習中，我們將建立一個完整的多容器應用，包含：
- **Flask Web 應用**：提供 API 和網頁介面
- **MySQL 資料庫**：儲存應用資料
- **phpMyAdmin**：資料庫管理介面

這個練習將展示 Docker Compose 在實際專案中的應用，讓您體驗多容器應用的完整開發流程。

### 🎯 練習目標
- 建立多容器應用架構
- 學習服務間的網路通訊
- 實作資料持久化
- 掌握 Docker Compose 的實際應用
- 學習多容器應用的管理和監控

### 📁 步驟 1：建立專案結構

首先建立專案目錄結構：

```bash
mkdir flask-mysql-app
cd flask-mysql-app

# 建立目錄結構
mkdir app
mkdir database
mkdir database/init
```

最終的專案結構：
```
flask-mysql-app/
├── docker-compose.yml
├── .env
├── app/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
└── database/
    └── init/
        └── init.sql
```

### 🐍 步驟 2：建立 Flask 應用

**建立 `app/requirements.txt`：**
```txt
Flask==2.3.3
mysql-connector-python==8.1.0
Werkzeug==2.3.7
```

**建立 `app/app.py`：**
```python
from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
import time

app = Flask(__name__)

# 資料庫連接配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'database'),
    'user': os.environ.get('DB_USER', 'appuser'),
    'password': os.environ.get('DB_PASSWORD', 'apppass'),
    'database': os.environ.get('DB_NAME', 'flask_app'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def get_db_connection():
    """建立資料庫連接，包含重試機制"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except mysql.connector.Error as e:
            print(f"資料庫連接失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # 等待 5 秒後重試
            else:
                raise

@app.route('/')
def home():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 查詢使用者資料
        cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('index.html', users=users)
    except Exception as e:
        return render_template('index.html', users=[], error=str(e))

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'success': False, 'error': '姓名和電子郵件為必填欄位'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'user_id': user_id, 'message': '使用者新增成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': time.time()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

**建立 `app/templates/index.html`：**
```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask + MySQL Docker Compose Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .form-section {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        input[type="text"], input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background: #3498db;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #2980b9;
        }
        .users-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .users-table th, .users-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .users-table th {
            background-color: #34495e;
            color: white;
        }
        .users-table tr:hover {
            background-color: #f5f5f5;
        }
        .error {
            color: #e74c3c;
            background: #fadbd8;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .success {
            color: #27ae60;
            background: #d5f4e6;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .api-links {
            margin-top: 30px;
            text-align: center;
        }
        .api-links a {
            display: inline-block;
            margin: 10px;
            padding: 10px 20px;
            background: #9b59b6;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        .api-links a:hover {
            background: #8e44ad;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐳 Flask + MySQL + Docker Compose</h1>
            <p>多容器應用實作示範</p>
        </div>
        
        {% if error %}
        <div class="error">
            <strong>錯誤：</strong> {{ error }}
        </div>
        {% endif %}
        
        <div class="form-section">
            <h3>新增使用者</h3>
            <form id="userForm">
                <div class="form-group">
                    <label for="name">姓名：</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">電子郵件：</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <button type="submit">新增使用者</button>
            </form>
            <div id="message"></div>
        </div>
        
        <div>
            <h3>使用者列表</h3>
            {% if users %}
            <table class="users-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>姓名</th>
                        <th>電子郵件</th>
                        <th>建立時間</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user[0] }}</td>
                        <td>{{ user[1] }}</td>
                        <td>{{ user[2] }}</td>
                        <td>{{ user[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>目前沒有使用者資料。</p>
            {% endif %}
        </div>
        
        <div class="api-links">
            <h3>API 端點測試：</h3>
            <a href="/api/users" target="_blank">查看使用者 API</a>
            <a href="/health" target="_blank">健康檢查</a>
            <a href="http://localhost:8081" target="_blank">phpMyAdmin</a>
        </div>
    </div>

    <script>
        document.getElementById('userForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const messageDiv = document.getElementById('message');
            
            try {
                const response = await fetch('/api/users', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, email })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    messageDiv.innerHTML = '<div class="success">' + result.message + '</div>';
                    document.getElementById('userForm').reset();
                    // 重新載入頁面以顯示新資料
                    setTimeout(() => location.reload(), 1000);
                } else {
                    messageDiv.innerHTML = '<div class="error">錯誤：' + result.error + '</div>';
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class="error">請求失敗：' + error.message + '</div>';
            }
        });
    </script>
</body>
</html>
```

**建立 `app/Dockerfile`：**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 建立非 root 使用者
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
```

### 🗄️ 步驟 3：建立資料庫初始化檔案

**建立 `database/init/init.sql`：**
```sql
-- 建立資料庫（如果不存在）
CREATE DATABASE IF NOT EXISTS flask_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用資料庫
USE flask_app;

-- 建立使用者表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入範例資料
INSERT INTO users (name, email) VALUES 
('張小明', 'ming@example.com'),
('李小華', 'hua@example.com'),
('王大同', 'wang@example.com')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 建立索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### 🐳 步驟 4：撰寫 docker-compose.yml

**建立 `.env` 檔案：**
```env
# 資料庫配置
MYSQL_ROOT_PASSWORD=rootpassword123
MYSQL_DATABASE=flask_app
MYSQL_USER=appuser
MYSQL_PASSWORD=apppass

# 應用程式配置
FLASK_ENV=development
PORT=5000

# phpMyAdmin 配置
PMA_HOST=database
PMA_PORT=3306
```

**建立 `docker-compose.yml`：**
```yaml
version: '3.8'

services:
  # MySQL 資料庫服務
  database:
    image: mysql:8.0
    container_name: flask-mysql-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      # 資料持久化
      - mysql_data:/var/lib/mysql
      # 初始化腳本
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # Flask Web 應用服務
  web:
    build: ./app
    container_name: flask-web-app
    restart: unless-stopped
    environment:
      DB_HOST: database
      DB_USER: ${MYSQL_USER}
      DB_PASSWORD: ${MYSQL_PASSWORD}
      DB_NAME: ${MYSQL_DATABASE}
      DB_PORT: 3306
      FLASK_ENV: ${FLASK_ENV}
      PORT: ${PORT}
    ports:
      - "8080:5000"
    volumes:
      # 開發時掛載代碼目錄（可選）
      - ./app:/app
    networks:
      - app-network
    depends_on:
      database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # phpMyAdmin 資料庫管理介面
  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    container_name: flask-phpmyadmin
    restart: unless-stopped
    environment:
      PMA_HOST: ${PMA_HOST}
      PMA_PORT: ${PMA_PORT}
      PMA_USER: ${MYSQL_USER}
      PMA_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    ports:
      - "8081:80"
    networks:
      - app-network
    depends_on:
      database:
        condition: service_healthy

# 定義網路
networks:
  app-network:
    driver: bridge
    name: flask-mysql-network

# 定義持久化卷
volumes:
  mysql_data:
    name: flask-mysql-data
```

### 🚀 步驟 5：啟動多容器應用

現在讓我們啟動完整的多容器應用：

```bash
# 確認檔案結構
ls -la

# 啟動所有服務（第一次會建立映像）
docker-compose up --build

# 或者在背景運行
docker-compose up -d --build
```

**查看服務狀態：**
```bash
# 查看所有服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs
docker-compose logs web        # 只看 web 服務日誌
docker-compose logs database   # 只看資料庫日誌

# 即時跟蹤日誌
docker-compose logs -f web
```

### 🧪 步驟 6：測試應用功能

#### 1. 測試 Web 介面
- 在 Play with Docker 中點擊端口 8080 連結
- 或在瀏覽器中訪問應用 URL
- 測試新增使用者功能
- 查看使用者列表

#### 2. 測試 API 端點
```bash
# 健康檢查
curl http://localhost:8080/health

# 查看所有使用者
curl http://localhost:8080/api/users

# 新增使用者
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"測試使用者","email":"test@example.com"}'
```

#### 3. 測試 phpMyAdmin
- 訪問 http://localhost:8081
- 使用以下憑證登入：
  - 伺服器：database
  - 使用者名稱：appuser
  - 密碼：apppass
- 瀏覽 flask_app 資料庫和 users 表

#### 4. 測試容器間通訊
```bash
# 進入 web 容器
docker-compose exec web bash

# 在容器內測試資料庫連接
ping database
nslookup database

# 離開容器
exit
```

### 🔧 步驟 7：管理和監控

#### 1. 服務管理
```bash
# 重啟特定服務
docker-compose restart web

# 停止特定服務
docker-compose stop database

# 重新建立並啟動服務
docker-compose up --build web

# 擴展服務實例
docker-compose up --scale web=2
```

#### 2. 資源監控
```bash
# 查看容器資源使用情況
docker stats

# 查看網路資訊
docker network ls
docker network inspect flask-mysql-network

# 查看卷資訊
docker volume ls
docker volume inspect flask-mysql-data
```

#### 3. 資料備份
```bash
# 備份資料庫
docker-compose exec database mysqldump -u root -p${MYSQL_ROOT_PASSWORD} flask_app > backup.sql

# 或者備份整個資料卷
docker run --rm -v flask-mysql-data:/data -v $(pwd):/backup alpine tar czf /backup/mysql-backup.tar.gz -C /data .
```

### 🛠️ 故障排除和常見問題

#### 1. 服務啟動失敗
```bash
# 查看詳細日誌
docker-compose logs --details

# 檢查服務狀態
docker-compose ps

# 重新建立有問題的服務
docker-compose up --build --force-recreate web
```

#### 2. 資料庫連接問題
```bash
# 檢查資料庫是否準備就緒
docker-compose exec database mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "SHOW DATABASES;"

# 測試網路連接
docker-compose exec web ping database

# 查看環境變數
docker-compose exec web env | grep DB_
```

#### 3. 端口衝突
```bash
# 檢查端口使用情況
netstat -tulpn | grep :8080

# 修改 docker-compose.yml 中的端口映射
# 例如：將 "8080:5000" 改為 "8090:5000"
```

#### 4. 卷掛載問題
```bash
# 檢查卷是否正確掛載
docker-compose exec database ls -la /var/lib/mysql

# 檢查初始化腳本是否執行
docker-compose exec database ls -la /docker-entrypoint-initdb.d/
```

#### 5. 權限問題
```bash
# 檢查檔案權限
ls -la app/
ls -la database/

# 修正權限（如果需要）
chmod +x app/app.py
chmod 644 database/init/init.sql
```

### 📈 進階練習

完成基本練習後，可以嘗試以下進階功能：

#### 1. 添加 Redis 快取服務
```yaml
# 在 docker-compose.yml 中添加
redis:
  image: redis:alpine
  container_name: flask-redis
  restart: unless-stopped
  ports:
    - "6379:6379"
  networks:
    - app-network
```

#### 2. 添加 Nginx 反向代理
```yaml
nginx:
  image: nginx:alpine
  container_name: flask-nginx
  restart: unless-stopped
  ports:
    - "80:80"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  networks:
    - app-network
  depends_on:
    - web
```

#### 3. 環境分離（開發/生產）
```bash
# 建立不同環境的 compose 檔案
# docker-compose.dev.yml - 開發環境
# docker-compose.prod.yml - 生產環境

# 使用特定環境啟動
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

#### 4. 監控和日誌管理
```yaml
# 添加 ELK Stack 或 Prometheus + Grafana
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 🔒 安全最佳實踐

#### 1. 環境變數管理
```bash
# 使用 Docker Secrets（Docker Swarm）
echo "mysecretpassword" | docker secret create db_password -

# 或使用外部密鑰管理工具
# 如 HashiCorp Vault、AWS Secrets Manager
```

#### 2. 網路安全
```yaml
# 建立隔離的網路
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 內部網路，無法訪問外部
```

#### 3. 容器安全
```dockerfile
# 在 Dockerfile 中使用非 root 使用者
RUN useradd --create-home --shell /bin/bash app
USER app

# 只暴露必要的端口
EXPOSE 5000
```

### 🚀 部署到生產環境

#### 1. Docker Swarm 部署
```bash
# 初始化 Swarm
docker swarm init

# 部署 stack
docker stack deploy -c docker-compose.yml flask-app
```

#### 2. Kubernetes 部署
```bash
# 使用 Kompose 轉換
kompose convert

# 或手動建立 Kubernetes manifests
kubectl apply -f k8s/
```

#### 3. 雲端部署
```bash
# AWS ECS
ecs-cli compose up

# Google Cloud Run
gcloud run deploy

# Azure Container Instances
az container create
```

### 🎉 練習總結

透過這個完整的實作練習，您已經學會了：

✅ **Docker Compose 基本概念**
- 多容器應用的編排和管理
- YAML 配置檔案的撰寫
- 服務間的依賴關係定義

✅ **實際應用開發**
- Flask Web 應用的容器化
- MySQL 資料庫的配置和初始化
- phpMyAdmin 管理介面的整合

✅ **網路和資料管理**
- 容器間的網路通訊
- 資料持久化和卷管理
- 環境變數的配置

✅ **運維和監控**
- 服務的啟動、停止和重啟
- 日誌查看和故障排除
- 健康檢查和監控

✅ **最佳實踐**
- 安全配置和權限管理
- 環境分離和配置管理
- 擴展性和可維護性

### 🧹 清理資源

完成練習後，清理所有資源：

```bash
# 停止並刪除所有服務
docker-compose down

# 刪除所有資源（包括卷和網路）
docker-compose down -v --remove-orphans

# 清理未使用的映像
docker image prune -a

# 清理系統（謹慎使用）
docker system prune -a --volumes
```

### 🎯 下一步學習建議

完成這個 Docker Compose 教學後，建議您繼續學習：

1. **Kubernetes 基礎**：學習容器編排的進階工具
2. **CI/CD 整合**：將 Docker 整合到持續整合/部署流程
3. **微服務架構**：使用 Docker 建立微服務應用
4. **監控和日誌**：學習 Prometheus、Grafana、ELK Stack
5. **安全實踐**：深入了解容器安全和最佳實踐

這個練習展示了 Docker Compose 在實際專案中的強大功能。掌握這些技能後，您就能夠：
- 快速建立和部署多容器應用
- 管理複雜的應用架構
- 實現開發、測試、生產環境的一致性
- 為進階的容器編排工具（如 Kubernetes）打下堅實基礎

恭喜您完成了 Docker 基礎教學的第四部分！🎊 您現在已經具備了使用 Docker Compose 管理多容器應用的能力，這是邁向現代化應用開發和部署的重要里程碑！