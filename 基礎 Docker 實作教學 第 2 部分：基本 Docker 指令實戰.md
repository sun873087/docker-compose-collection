# 基礎 Docker 實作教學(第二部分：基本 Docker 指令實戰 )

課程時間：30 分鐘

- 映像檔管理指令
- 容器運行與交互
- 容器管理指令
- 實用指令與技巧

---

## 映像檔管理指令

### 1. 搜尋映像檔
```bash
# 在 Docker Hub 搜尋映像檔
docker search nginx
docker search ubuntu
```

### 2. 下載映像檔
```bash
# 下載最新版本的映像檔
docker pull nginx
docker pull ubuntu

# 下載指定版本的映像檔
docker pull nginx:1.21
docker pull ubuntu:20.04
```

### 3. 查看本地映像檔
```bash
# 列出所有本地映像檔
docker images

# 查看映像檔詳細資訊
docker inspect nginx
```

### 4. 刪除映像檔
```bash
# 刪除指定映像檔
docker rmi nginx:latest

# 強制刪除映像檔
docker rmi -f nginx:latest

# 刪除所有未使用的映像檔
docker image prune -a
```

---

## 容器運行與交互

### 1. 基本容器運行
```bash
# 運行一個簡單的容器
docker run hello-world

# 運行並進入互動模式
docker run -it ubuntu bash
cat /etc/os-release # 查看 Ubuntu 版本
exit # 退出容器

# 在背景運行容器
docker run --name myweb -d nginx
# 查看運行中的容器
docker ps
# 查看所有容器（包括停止的）
docker ps -a

# 停止容器
docker stop myweb
# 刪除容器
docker rm myweb
```

### 2. 容器端口映射
```bash
# 映射端口到主機
docker run -d --name myweb -p 8080:80 nginx

# 檢查端口映射
docker port myweb

docker stop myweb
docker rm myweb
```

### 3. 容器與主機檔案交換
```bash
# 掛載主機目錄到容器 -v <host_path>:<container_path>
docker run -d --name myweb -v ./dockercmd/data/html:/usr/share/nginx/html -p 8080:80 nginx

# 複製檔案到容器 cp <source_path> <container_id_or_name>:<destination_path>
docker cp ./dockercmd/docker.html myweb:/usr/share/nginx/html/index.html
docker cp ./dockercmd/index.html myweb:/usr/share/nginx/html/index.html

# 從容器複製檔案 cp <container_id_or_name>:<source_path> <destination_path>
docker cp myweb:/usr/share/nginx/html/index.html ./dockercmd/container_index.html
```

### 4. 進入運行中的容器
```bash
# 進入容器的 bash 環境 exec -it <container_id_or_name> bash
docker exec -it myweb bash
cat /etc/os-release # 查看 Ubuntu 版本
exit # 退出容器

# 在容器中執行單一命令 exec <container_id_or_name> <command>
docker exec myweb ls -la
```

---

## 容器管理指令

### 1. 查看容器狀態
```bash
# 查看運行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 查看容器詳細資訊 inspect <container_id_or_name>
docker inspect myweb
```

### 2. 容器生命週期管理
```bash
# 停止運行中的容器 stop <container_id_or_name>
# 停止容器會發送 SIGTERM 信號，然後等待一段時間後發送 SIGKILL
docker stop myweb

# 查看所有容器狀態
docker ps -a 

# 啟動已停止的容器 start <container_id_or_name>
docker start myweb

# 重啟容器 restart <container_id_or_name>
docker restart myweb

# 暫停容器 pause <container_id_or_name>
# 暫停與停止的區別在於暫停會凍結容器的進程，而停止會終止容器的運行
docker pause myweb

# 恢復暫停的容器 unpause <container_id_or_name>
docker unpause myweb
```

### 3. 容器日誌與監控
```bash
# 查看容器日誌 logs <container_id_or_name>
docker logs myweb

# 即時查看日誌 logs -f <container_id_or_name>
docker logs -f myweb

# 查看容器資源使用情況 stats <container_id_or_name>
# 這會顯示 CPU、記憶體、網路等使用情況
docker stats myweb
```

### 4. 刪除容器
```bash
# 刪除停止的容器 rm <container_id_or_name>
docker rm myweb

# 刪除所有停止的容器
docker container prune
```

---

## 實用指令與技巧

### 1. 系統資訊與清理
```bash
# 查看 Docker 系統資訊
docker system info

# 查看 Docker 版本
docker version

# 清理未使用的資源
docker system prune

# 清理所有未使用的資源（包括未使用的映像檔）
docker system prune -a
```

### 2. 容器命名與標籤
```bash
# 為容器指定名稱
docker run --name my-nginx -d nginx

# 為映像檔添加標籤
docker tag nginx:latest my-nginx:v1.0

# 使用自定義名稱運行容器
docker run --name web-server -d -p 80:80 nginx

docker stop $(docker ps -q)
docker container prune
```

### 3. 環境變數與配置
```bash
# 設定環境變數 -e <key>=<value>
docker run --name my-mysql -e MYSQL_ROOT_PASSWORD=secret -d mysql

# 從檔案讀取環境變數 --env-file <file>
docker run --name my-mysql --env-file ./dockercmd/mysql.env -d mysql

# 查看容器環境變數 exec <container_id_or_name> env
docker exec my-mysql env
```

### 4. 實用組合指令
```bash
# 停止並刪除所有容器
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)

# 一鍵清理系統
docker system prune -af --volumes
```

### 🔧 課堂練習
1. 下載並運行一個 nginx 容器，名稱為 web，映射到本機 8080 端口
2. 進入容器看首頁內容
3. 查看容器日誌和資源使用情況
4. 停止 container
5. 清理所有未使用的容器
6. 清理所有未使用的映像檔

```bash
# 1. 下載並運行一個 nginx 容器，名稱為 web，映射到本機 8080 端口
docker run --name web -d -p 8080:80 nginx

# 2. 進入容器看首頁內容
docker exec -it web /bin/bash
# 在容器內部
cat /usr/share/nginx/html/index.html
# 退出容器內部
exit

# 3. 查看容器日誌和資源使用情況
docker logs web
docker stats web # 使用 ctrl + c 停止監控

# 4. 停止 container
docker stop web

# 5. 清理所有未使用的容器
docker container prune

# 6. 清理所有未使用的映像檔
docker image prune -a
```