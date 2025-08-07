# [Keycloak] docker 安裝

採用的映象檔是 bitnami/keycloak ，因為我需要使用網址來區分服務(同一個 port 的情況下)，所以採取反向代理的方式，一方面讓之後要部屬其他應用、加上憑證、等等操作都交給 nginx 比較方便。

1. 建立 docker 網路 mynetwork，如果設定其他名稱，以下步驟再自行調整對應。
   ```bash
   docker network create mynetwork
   ```
2. 建立 docker-compose 環境 keycloak/.env
   ```bash
   cp .env.example .env
   ```
3. 啓動 keycloak
   ```bash
   docker compose up -d
   ```
4. 啓動 nginx
   ```bash
   cd nginx
   docker compose up -d
   ```
5. 設置 hostname
   - windows 加入 C:\Windows\System32\drivers\etc\host
   - linux 加入 /etc/hosts   
   ```text
   <your ip> keycloak.docker.vm
   ```