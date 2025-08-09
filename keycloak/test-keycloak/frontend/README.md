# Keycloak React 前端測試應用程式

這是一個用於測試 Keycloak 前端登入流程的 React TypeScript 應用程式。

## 功能特色

- ✅ Keycloak JavaScript 適配器整合
- ✅ React Context API 用於狀態管理
- ✅ 受保護路由實作
- ✅ 自動 Token 更新
- ✅ TypeScript 支援
- ✅ 響應式導航列

## 專案結構

```
src/
├── components/
│   ├── Navigation.tsx       # 導航列組件
│   └── ProtectedRoute.tsx   # 受保護路由組件
├── pages/
│   ├── Home.tsx            # 首頁
│   └── Protected.tsx       # 受保護頁面
├── keycloak.ts             # Keycloak 配置
├── KeycloakProvider.tsx    # Keycloak Context Provider
├── App.tsx                 # 主應用程式
└── index.tsx              # 應用程式入口點
```

## 設定說明

### 1. Keycloak 配置

編輯 `src/keycloak.ts` 文件，更新以下配置：

```typescript
const keycloak = new Keycloak({
  url: 'http://localhost:8080',  // 你的 Keycloak 伺服器 URL
  realm: 'myrealm',             // 你的 realm 名稱
  clientId: 'myclient',         // 你的 client ID
});
```

### 2. Keycloak 伺服器設定

確保你的 Keycloak 伺服器已設定以下項目：

1. **Realm**: 建立一個 realm（例如：myrealm）
2. **Client**: 建立一個公開客戶端（例如：myclient）
   - Client Type: `public`
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
3. **User**: 建立測試用戶帳號

## 安裝與執行

```bash
# 安裝依賴套件
npm install

# 啟動開發伺服器
npm start
```

應用程式將在 `http://localhost:3000` 上運行。

## 功能測試

1. **首頁** (`/`): 
   - 顯示當前認證狀態
   - 顯示使用者資訊（如果已登入）
   - 提供 Token 檢視功能

2. **受保護頁面** (`/protected`):
   - 需要登入才能訪問
   - 顯示使用者詳細資訊
   - 提供模擬 API 呼叫功能

3. **導航功能**:
   - 登入/登出按鈕
   - 動態顯示使用者名稱
   - 響應式設計

## 故障排除

### 常見問題

1. **CORS 錯誤**: 
   - 確保 Keycloak 客戶端設定中的 Web origins 包含 `http://localhost:3000`

2. **認證失敗**: 
   - 檢查 Keycloak 伺服器是否運行在正確的 URL
   - 確認 realm 和 clientId 設定正確

3. **Token 過期**: 
   - 應用程式會自動更新 token
   - 如果更新失敗，會自動登出

### 除錯

開啟瀏覽器開發者工具的 Console 頁籤查看詳細的錯誤訊息和 Token 資訊。

## 依賴套件

- `react`: React 框架
- `react-router-dom`: 路由管理
- `keycloak-js`: Keycloak JavaScript 適配器
- `typescript`: TypeScript 支援