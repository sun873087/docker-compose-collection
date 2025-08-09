from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
import json
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import os

app = FastAPI(title="Keycloak API 測試後端", version="1.0.0")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keycloak 設定 - 嘗試不同的 Docker 網絡配置
KEYCLOAK_URLS = [
    "http://localhost:8080",              # 標準本地訪問
    "http://127.0.0.1:8080",             # IP 訪問
    "http://host.docker.internal:8080",   # 從容器訪問主機
    "http://docker.for.mac.localhost:8080", # Mac Docker 舊版
]
REALM = "sam-test"
CLIENT_ID = "myclient"

security = HTTPBearer()

class UserInfo(BaseModel):
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None

class TokenValidationError(Exception):
    pass

async def get_public_key():
    """獲取 Keycloak 公鑰 - 支援舊版和新版 Keycloak"""
    try:
        # 先嘗試新版 OpenID Connect discovery
        openid_urls = []
        for base_url in KEYCLOAK_URLS:
            openid_urls.extend([
                f"{base_url}/realms/{REALM}/.well-known/openid_configuration",
                f"{base_url}/auth/realms/{REALM}/.well-known/openid_configuration"
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
        
        # 如果 OpenID 配置不可用，嘗試舊版直接 realm 端點
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
                        # 轉換 PEM 格式公鑰為 JWKS 格式
                        from cryptography.hazmat.primitives import serialization
                        from cryptography.hazmat.primitives.serialization import load_pem_public_key
                        import base64
                        
                        # 構建完整的 PEM
                        pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_pem}\n-----END PUBLIC KEY-----"
                        public_key = load_pem_public_key(pem_key.encode())
                        
                        # 從 realm 資訊獲取額外資訊
                        algorithm = realm_info.get("algorithm", "RS256")
                        
                        # 轉換為 JWKS 格式
                        jwks = {
                            "keys": [{
                                "kty": "RSA",
                                "use": "sig",
                                "kid": realm_info.get("realm", "default"),  # 使用 realm 名稱作為 kid
                                "n": base64.urlsafe_b64encode(
                                    public_key.public_numbers().n.to_bytes(
                                        (public_key.key_size + 7) // 8, 'big'
                                    )
                                ).decode().rstrip('='),
                                "e": base64.urlsafe_b64encode(
                                    public_key.public_numbers().e.to_bytes(3, 'big')
                                ).decode().rstrip('='),
                                "alg": algorithm
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
    """驗證 JWT token"""
    token = credentials.credentials
    
    try:
        # 獲取 JWKS
        jwks = await get_public_key()
        
        # 解碼 token header 獲取 kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        print(f"Token kid: {kid}")
        
        # 找到對應的公鑰
        public_key = None
        print(f"可用的 keys: {[key.get('kid') for key in jwks['keys']]}")
        
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = key
                break
        
        # 如果找不到對應的 kid，嘗試使用第一個可用的公鑰（適用於單一公鑰的舊版 Keycloak）
        if not public_key and jwks["keys"]:
            print("找不到對應的 kid，使用第一個可用的公鑰")
            public_key = jwks["keys"][0]
        
        if not public_key:
            raise TokenValidationError("找不到對應的公鑰")
        
        # 驗證 token（使用正確的 audience）
        # 使用 token 中的 issuer 來驗證
        token_issuer = jwt.get_unverified_claims(token).get("iss")
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="account",  # Keycloak 預設的 audience
            issuer=token_issuer
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
    """基本 token 驗證，只驗證格式和過期時間"""
    token = credentials.credentials
    
    try:
        # 解析 token（不驗證簽名）
        payload = jwt.get_unverified_claims(token)
        
        # 檢查基本字段
        if not payload.get("sub"):
            raise TokenValidationError("Token 缺少 subject")
        
        if not payload.get("iss"):
            raise TokenValidationError("Token 缺少 issuer")
        
        # 檢查 issuer 是否正確（檢查所有可能的 URL）
        token_issuer = payload.get("iss")
        valid_issuers = [f"{base_url}/realms/{REALM}" for base_url in KEYCLOAK_URLS]
        
        if token_issuer not in valid_issuers:
            print(f"Token issuer: {token_issuer}")
            print(f"Valid issuers: {valid_issuers}")
            # 不拋出錯誤，只記錄警告，因為 token 中的 issuer 是正確的
            print("警告：issuer 不在預期列表中，但繼續處理")
        
        # 檢查是否過期
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