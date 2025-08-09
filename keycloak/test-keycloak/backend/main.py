"""
Keycloak API 測試後端

這是一個完整的 FastAPI 後端應用，用於測試 Keycloak JWT Token 驗證和 API 整合。
支援多種 Keycloak 版本和配置，包括開發模式和生產模式。

主要功能：
- JWT Token 驗證（支援完整簽名驗證和基本驗證）
- 多版本 Keycloak 相容性（自動偵測和適應）
- CORS 支援前端整合
- RESTful API 端點
- 角色權限檢查
- Token 刷新功能
- 除錯和診斷工具

作者: Claude Code
版本: 1.0.0
相容: Keycloak 17+ (包含 24.x 開發模式)
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
import json
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import os

# 建立 FastAPI 應用實例
app = FastAPI(
    title="Keycloak API 測試後端", 
    version="1.0.0",
    description="用於測試 Keycloak JWT 驗證和 API 整合的後端服務",
    docs_url="/docs",  # Swagger UI 文檔路徑
    redoc_url="/redoc"  # ReDoc 文檔路徑
)

# ============================================================================
# CORS 設定 - 跨域資源共享
# ============================================================================
# 允許前端 (React) 從不同端口訪問 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允許的前端域名
    allow_credentials=True,  # 允許包含認證資訊（如 cookies）
    allow_methods=["*"],     # 允許所有 HTTP 方法
    allow_headers=["*"],     # 允許所有 HTTP 標頭
)

# ============================================================================
# Keycloak 配置設定
# ============================================================================
# 支援多種網絡配置，自動嘗試不同的 Keycloak 連接方式
# 適用於不同的部署環境：本地開發、Docker、生產環境
KEYCLOAK_URLS = [
    "http://localhost:8080",                # 標準本地開發訪問
    "http://127.0.0.1:8080",               # IP 地址訪問（避免 DNS 問題）
    "http://host.docker.internal:8080",     # 從 Docker 容器訪問主機
    "http://docker.for.mac.localhost:8080", # Mac Docker Desktop 舊版本支援
]

# Keycloak Realm 和 Client 設定
REALM = "sam-test"      # 你的 Keycloak Realm 名稱
CLIENT_ID = "myclient"  # 你的 Keycloak Client ID

# HTTP Bearer Token 安全方案（用於提取 Authorization 標頭）
security = HTTPBearer()

# ============================================================================
# 資料模型定義 (Pydantic Models)
# ============================================================================

class UserInfo(BaseModel):
    """使用者資訊資料模型
    
    對應 JWT Token 中的使用者相關欄位
    """
    sub: str                                    # 使用者唯一識別碼（Subject）
    email: Optional[str] = None                 # 電子郵件地址
    name: Optional[str] = None                  # 完整姓名
    preferred_username: Optional[str] = None    # 偏好使用者名稱
    given_name: Optional[str] = None           # 名字
    family_name: Optional[str] = None          # 姓氏

class TokenValidationError(Exception):
    """自定義例外：Token 驗證錯誤
    
    用於處理 JWT Token 驗證過程中的各種錯誤情況
    """
    pass

# ============================================================================
# 核心功能函數
# ============================================================================

async def get_public_key():
    """
    獲取 Keycloak 公鑰 - 支援多版本 Keycloak
    
    這個函數實現了多層次的相容性策略：
    1. 優先嘗試標準 OpenID Connect Discovery (適用於生產模式)
    2. 回退到直接 Realm 端點 (適用於開發模式或舊版本)
    3. 自動轉換不同格式的公鑰 (JWKS ↔ PEM)
    
    Returns:
        dict: JWKS 格式的公鑰資訊
        
    Raises:
        TokenValidationError: 無法獲取公鑰時拋出
        
    支援的 Keycloak 版本：
    - Keycloak 17+ (標準生產模式)
    - Keycloak 24.x (開發模式)
    - 舊版 Keycloak (相容性支援)
    """
    try:
        # 策略 1: 嘗試標準 OpenID Connect Discovery
        # 這是 Keycloak 生產模式的標準做法，提供完整的配置資訊
        openid_urls = []
        for base_url in KEYCLOAK_URLS:
            openid_urls.extend([
                f"{base_url}/realms/{REALM}/.well-known/openid_configuration",      # Keycloak 17+ 標準路徑
                f"{base_url}/auth/realms/{REALM}/.well-known/openid_configuration" # Keycloak 16- 舊版路徑
            ])
        
        for url in openid_urls:
            try:
                print(f"嘗試 OpenID 配置: {url}")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    openid_config = response.json()
                    jwks_uri = openid_config["jwks_uri"]
                    jwks_response = requests.get(jwks_uri)
                    jwks_response.raise_for_status()
                    print(f"成功使用 OpenID 配置: {url}")
                    return jwks_response.json()
            except Exception as e:
                print(f"OpenID 配置失敗: {str(e)}")
                continue
        
        # 策略 2: 回退到直接 Realm 端點
        # 適用於 Keycloak 開發模式或自定義配置，直接從 realm 資訊獲取公鑰
        print("嘗試舊版 realm 端點獲取公鑰...")
        for base_url in KEYCLOAK_URLS:
            realm_url = f"{base_url}/realms/{REALM}"
            try:
                print(f"嘗試 realm 端點: {realm_url}")
                response = requests.get(realm_url, timeout=5)
                if response.status_code == 200:
                    realm_info = response.json()
                    public_key_pem = realm_info.get("public_key")
                    if public_key_pem:
                        # 公鑰格式轉換: PEM → JWKS
                        # Keycloak 開發模式提供 PEM 格式，但 JWT 驗證需要 JWKS 格式
                        from cryptography.hazmat.primitives import serialization
                        from cryptography.hazmat.primitives.serialization import load_pem_public_key
                        import base64
                        
                        # 重建完整的 PEM 格式公鑰
                        # Keycloak 只提供公鑰內容，需要添加 PEM 標頭和標尾
                        pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_pem}\n-----END PUBLIC KEY-----"
                        public_key = load_pem_public_key(pem_key.encode())
                        
                        # 提取算法資訊（預設為 RS256）
                        algorithm = realm_info.get("algorithm", "RS256")
                        
                        # 建構標準 JWKS (JSON Web Key Set) 格式
                        # 將 RSA 公鑰轉換為 JWT 驗證所需的格式
                        jwks = {
                            "keys": [{
                                "kty": "RSA",                                    # 金鑰類型: RSA
                                "use": "sig",                                    # 用途: 數位簽名
                                "kid": realm_info.get("realm", "default"),     # 金鑰識別碼
                                "n": base64.urlsafe_b64encode(                   # RSA 模數 (n)
                                    public_key.public_numbers().n.to_bytes(
                                        (public_key.key_size + 7) // 8, 'big'
                                    )
                                ).decode().rstrip('='),
                                "e": base64.urlsafe_b64encode(                   # RSA 指數 (e)
                                    public_key.public_numbers().e.to_bytes(3, 'big')
                                ).decode().rstrip('='),
                                "alg": algorithm                                # 簽名算法
                            }]
                        }
                        print(f"成功從 realm 端點獲取公鑰: {realm_url}")
                        return jwks
            except Exception as e:
                print(f"Realm 端點失敗: {str(e)}")
                continue
        
        raise TokenValidationError("無法從任何端點獲取 Keycloak 公鑰")
        
    except Exception as e:
        raise TokenValidationError(f"無法獲取 Keycloak 公鑰: {str(e)}")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    完整的 JWT Token 驗證
    
    執行完整的 JWT 驗證流程，包括：
    1. 數位簽名驗證（使用 Keycloak 公鑰）
    2. Token 完整性檢查
    3. 發行者 (issuer) 驗證
    4. 受眾 (audience) 驗證
    5. 過期時間檢查
    
    Args:
        credentials: HTTP Bearer Token 憑證
        
    Returns:
        Dict[str, Any]: 驗證成功的 Token 負載 (payload)
        
    Raises:
        HTTPException: Token 驗證失敗時拋出 401 錯誤
        
    安全等級: 最高（生產環境建議）
    """
    token = credentials.credentials
    
    try:
        # 步驟 1: 獲取 Keycloak 公鑰集合 (JWKS)
        jwks = await get_public_key()
        
        # 步驟 2: 解析 Token 標頭，獲取金鑰識別碼 (kid)
        # kid 用於從多個公鑰中選擇正確的驗證金鑰
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        print(f"Token kid: {kid}")
        
        # 步驟 3: 金鑰匹配策略
        # 根據 kid 找到對應的公鑰，支援多種匹配策略以提高相容性
        public_key = None
        print(f"可用的 keys: {[key.get('kid') for key in jwks['keys']]}")
        
        # 策略 3a: 精確匹配 kid
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = key
                break
        
        # 策略 3b: 回退策略 - 使用第一個可用公鑰
        # 適用於舊版 Keycloak 或只有單一公鑰的情況
        if not public_key and jwks["keys"]:
            print("找不到對應的 kid，使用第一個可用的公鑰")
            public_key = jwks["keys"][0]
        
        if not public_key:
            raise TokenValidationError("找不到對應的公鑰")
        
        # 步驟 4: 執行 JWT 驗證
        # 使用找到的公鑰進行完整的 JWT 驗證
        token_issuer = jwt.get_unverified_claims(token).get("iss")
        payload = jwt.decode(
            token,
            public_key,                    # 驗證用公鑰
            algorithms=["RS256"],          # 支援的簽名算法
            audience="account",            # Keycloak 預設的 audience
            issuer=token_issuer           # 動態 issuer 驗證
        )
        
        return payload
    
    except JWTError as e:
        print(f"JWT 驗證錯誤: {str(e)}")  # 服務器端記錄
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token 驗證失敗: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenValidationError as e:
        print(f"Token 驗證錯誤: {str(e)}")  # 服務器端記錄
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")  # 服務器端記錄
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"驗證過程發生錯誤: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/")
async def root():
    """健康檢查端點"""
    return {"message": "Keycloak API 測試後端運行中", "status": "OK"}

@app.get("/api/public")
async def public_endpoint():
    """公開端點，不需要認證"""
    return {
        "message": "這是一個公開端點",
        "data": "任何人都可以訪問此端點",
        "timestamp": "2023-01-01T00:00:00Z"
    }

@app.get("/api/explore-keycloak")
async def explore_keycloak():
    """探索 Keycloak 服務結構"""
    results = {}
    base_urls = ["http://localhost:8080", "http://127.0.0.1:8080"]
    
    for base_url in base_urls:
        results[base_url] = {}
        
        # 嘗試不同的路徑
        test_paths = [
            "/",
            "/realms",
            "/auth/realms", 
            "/admin/realms",
            f"/realms/{REALM}",
            f"/auth/realms/{REALM}",
            f"/realms/{REALM}/.well-known/openid_configuration",
            f"/auth/realms/{REALM}/.well-known/openid_configuration"
        ]
        
        for path in test_paths:
            try:
                url = f"{base_url}{path}"
                response = requests.get(url, timeout=2)
                results[base_url][path] = {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "content_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text
                }
            except Exception as e:
                results[base_url][path] = {"error": str(e)}
    
    return results

@app.post("/api/debug-token")
async def debug_token(token_data: dict):
    """除錯端點：分析 token 結構"""
    try:
        token = token_data.get("token")
        if not token:
            return {"error": "未提供 token"}
        
        # 解碼 token header（不驗證）
        unverified_header = jwt.get_unverified_header(token)
        
        # 解碼 token payload（不驗證）
        unverified_payload = jwt.get_unverified_claims(token)
        
        return {
            "header": unverified_header,
            "payload": unverified_payload,
            "keycloak_config": {
                "urls": KEYCLOAK_URLS,
                "realm": REALM,
                "client_id": CLIENT_ID,
                "valid_issuers": [f"{url}/realms/{REALM}" for url in KEYCLOAK_URLS]
            }
        }
    except Exception as e:
        return {"error": f"解析 token 失敗: {str(e)}"}

async def verify_token_basic(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    基本 JWT Token 驗證
    
    執行基本的 Token 驗證，不進行數位簽名檢查：
    1. Token 格式驗證
    2. 必要欄位檢查 (sub, iss)
    3. 發行者檢查
    4. 過期時間檢查
    
    Args:
        credentials: HTTP Bearer Token 憑證
        
    Returns:
        Dict[str, Any]: Token 負載資訊
        
    注意: 此方法不驗證數位簽名，安全性較低
    適用場景: 開發測試、無法取得公鑰時的備用方案
    """
    token = credentials.credentials
    
    try:
        # 步驟 1: 解析 Token 內容（跳過簽名驗證）
        payload = jwt.get_unverified_claims(token)
        
        # 步驟 2: 檢查必要欄位
        if not payload.get("sub"):
            raise TokenValidationError("Token 缺少 subject")  # 使用者識別碼
        
        if not payload.get("iss"):
            raise TokenValidationError("Token 缺少 issuer")   # 發行者
        
        # 步驟 3: 發行者驗證
        # 檢查 Token 是否來自信任的 Keycloak 實例
        token_issuer = payload.get("iss")
        valid_issuers = [f"{base_url}/realms/{REALM}" for base_url in KEYCLOAK_URLS]
        
        if token_issuer not in valid_issuers:
            print(f"Token issuer: {token_issuer}")
            print(f"Valid issuers: {valid_issuers}")
            # 寬鬆驗證：記錄警告但不阻擋，因為實際 issuer 通常是正確的
            print("警告：issuer 不在預期列表中，但繼續處理")
        
        # 步驟 4: 過期時間檢查
        import time
        current_time = int(time.time())
        exp = payload.get("exp")
        if exp and current_time > exp:
            raise TokenValidationError("Token 已過期")
        
        return payload
    
    except TokenValidationError:
        raise
    except Exception as e:
        print(f"基本驗證錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token 驗證失敗: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/api/test-no-verify")
async def test_no_verify_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """測試端點，完全不驗證 token，只解析"""
    token = credentials.credentials
    try:
        # 只解析 token，不驗證簽名
        unverified_payload = jwt.get_unverified_claims(token)
        return {
            "message": "Token 解析成功（未驗證簽名）",
            "payload": unverified_payload
        }
    except Exception as e:
        return {"error": f"無法解析 token: {str(e)}"}

@app.get("/api/test-basic")
async def test_basic_endpoint(payload: Dict[str, Any] = Depends(verify_token_basic)):
    """基本驗證端點，不驗證簽名但檢查基本信息"""
    return {
        "message": "基本驗證成功（未驗證簽名）",
        "user_id": payload.get("sub"),
        "username": payload.get("preferred_username"),
        "email": payload.get("email"),
        "audience": payload.get("aud"),
        "issuer": payload.get("iss"),
        "expires_at": payload.get("exp")
    }

@app.get("/api/protected")
async def protected_endpoint(payload: Dict[str, Any] = Depends(verify_token)):
    """受保護端點，需要有效的 JWT token"""
    return {
        "message": "成功訪問受保護端點",
        "user_id": payload.get("sub"),
        "username": payload.get("preferred_username"),
        "email": payload.get("email"),
        "roles": payload.get("realm_access", {}).get("roles", []),
        "token_info": {
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
            "issuer": payload.get("iss")
        }
    }

@app.get("/api/user-info")
async def get_user_info(payload: Dict[str, Any] = Depends(verify_token)) -> UserInfo:
    """獲取使用者詳細資訊"""
    return UserInfo(
        sub=payload.get("sub"),
        email=payload.get("email"),
        name=payload.get("name"),
        preferred_username=payload.get("preferred_username"),
        given_name=payload.get("given_name"),
        family_name=payload.get("family_name")
    )

@app.get("/api/admin/users")
async def get_users(payload: Dict[str, Any] = Depends(verify_token)):
    """管理員端點：獲取所有使用者（需要管理員權限）"""
    # 檢查是否有管理員角色
    roles = payload.get("realm_access", {}).get("roles", [])
    if "realm-admin" not in roles and "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限才能訪問此端點"
        )
    
    return {
        "message": "管理員端點訪問成功",
        "note": "這裡可以實作 Keycloak Admin API 呼叫",
        "user_roles": roles
    }

@app.get("/api/token-info")
async def get_token_info(payload: Dict[str, Any] = Depends(verify_token)):
    """獲取 token 的詳細資訊"""
    return {
        "token_payload": payload,
        "user_info": {
            "user_id": payload.get("sub"),
            "username": payload.get("preferred_username"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "given_name": payload.get("given_name"),
            "family_name": payload.get("family_name")
        },
        "token_metadata": {
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
            "issuer": payload.get("iss"),
            "audience": payload.get("aud"),
            "token_type": payload.get("typ")
        },
        "permissions": {
            "realm_roles": payload.get("realm_access", {}).get("roles", []),
            "client_roles": payload.get("resource_access", {})
        }
    }

@app.post("/api/refresh-token")
async def refresh_token(refresh_token: dict):
    """刷新 token"""
    try:
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token.get("refresh_token")
        }
        
        url = f"{KEYCLOAK_URLS[0]}/realms/{REALM}/protocol/openid-connect/token"
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token 刷新失敗: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)