#!/bin/bash

# 設定域名變數
DOMAIN="gitlab.samcheng.home"

# 指定存放憑證的目錄
CERT_DIR="./data/certs"

# 如果目錄不存在，則創建它
mkdir -p "${CERT_DIR}"

# 生成自簽名 SSL 憑證
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "${CERT_DIR}/${DOMAIN}.key" \
  -out "${CERT_DIR}/${DOMAIN}.crt" \
  -subj "/CN=${DOMAIN}"

echo "自簽名憑證和私鑰已生成並移動到 ${CERT_DIR} 目錄："
echo "憑證文件：${CERT_DIR}/${DOMAIN}.crt"
echo "私鑰文件：${CERT_DIR}/${DOMAIN}.key"
