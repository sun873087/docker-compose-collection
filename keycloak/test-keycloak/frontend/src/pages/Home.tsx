import React from 'react';
import { useKeycloak } from '../KeycloakProvider';

const Home: React.FC = () => {
  const { isAuthenticated, username, token } = useKeycloak();

  return (
    <div style={{ padding: '20px' }}>
      <h1>Keycloak React 整合測試</h1>
      
      <div style={{ margin: '20px 0' }}>
        <h2>認證狀態</h2>
        <p>已登入: {isAuthenticated ? '是' : '否'}</p>
        {isAuthenticated && (
          <>
            <p>使用者名稱: {username}</p>
            <p>Token 存在: {token ? '是' : '否'}</p>
          </>
        )}
      </div>

      <div style={{ margin: '20px 0' }}>
        <h2>功能說明</h2>
        <ul>
          <li>首頁: 顯示當前認證狀態</li>
          <li>受保護頁面: 需要登入才能訪問</li>
          <li>登入/登出功能: 透過 Keycloak 進行身份驗證</li>
        </ul>
      </div>

      {token && (
        <div style={{ margin: '20px 0' }}>
          <h3>Token 資訊 (除錯用)</h3>
          <details>
            <summary>點擊查看 Token</summary>
            <pre style={{ 
              backgroundColor: '#f8f9fa', 
              padding: '10px', 
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px'
            }}>
              {token}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default Home;