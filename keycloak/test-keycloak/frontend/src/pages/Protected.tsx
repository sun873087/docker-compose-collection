import React, { useState } from 'react';
import { useKeycloak } from '../KeycloakProvider';
import ProtectedRoute from '../components/ProtectedRoute';

const ProtectedPage: React.FC = () => {
  const { username, token } = useKeycloak();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const callProtectedAPI = async () => {
    if (!token) {
      setError('沒有可用的 Token');
      return;
    }

    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/protected', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API 呼叫失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  const callUserInfoAPI = async () => {
    if (!token) {
      setError('沒有可用的 Token');
      return;
    }

    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/user-info', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API 呼叫失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  const callTokenInfoAPI = async () => {
    if (!token) {
      setError('沒有可用的 Token');
      return;
    }

    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/token-info', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API 呼叫失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  const debugToken = async () => {
    if (!token) {
      setError('沒有可用的 Token');
      return;
    }

    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/debug-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
      });

      if (!response.ok) {
        throw new Error(`API 呼叫失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  const testNoVerify = async () => {
    if (!token) {
      setError('沒有可用的 Token');
      return;
    }

    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/test-no-verify', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API 呼叫失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  const testBasic = async () => {
    if (!token) {
      setError('沒有可用的 Token');
      return;
    }

    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/test-basic', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API 呼叫失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div style={{ padding: '20px' }}>
        <h1>受保護的頁面</h1>
        <p>恭喜！你已經成功登入並訪問了受保護的頁面。</p>
        
        <div style={{ margin: '20px 0' }}>
          <h2>使用者資訊</h2>
          <p>使用者名稱: {username}</p>
          <p>認證狀態: 已登入</p>
        </div>

        <div style={{ margin: '20px 0' }}>
          <h2>可用操作</h2>
          <ul>
            <li>查看個人資料</li>
            <li>訪問受保護的 API</li>
            <li>執行需要認證的操作</li>
          </ul>
        </div>

        <div style={{ margin: '20px 0' }}>
          <h3>後端 API 測試</h3>
          <div style={{ marginBottom: '10px' }}>
            <button
              onClick={callProtectedAPI}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#6c757d' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginRight: '10px'
              }}
            >
              {loading ? '呼叫中...' : '測試受保護 API'}
            </button>
            
            <button
              onClick={callUserInfoAPI}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#6c757d' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginRight: '10px'
              }}
            >
              {loading ? '呼叫中...' : '獲取使用者資訊'}
            </button>
            
            <button
              onClick={callTokenInfoAPI}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#6c757d' : '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginRight: '10px'
              }}
            >
              {loading ? '呼叫中...' : '獲取 Token 資訊'}
            </button>
            
            <button
              onClick={debugToken}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#6c757d' : '#ffc107',
                color: loading ? 'white' : '#212529',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginRight: '10px'
              }}
            >
              {loading ? '呼叫中...' : '🐛 除錯 Token'}
            </button>
            
            <button
              onClick={testNoVerify}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#6c757d' : '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginRight: '10px'
              }}
            >
              {loading ? '呼叫中...' : '🔓 測試不驗證'}
            </button>
            
            <button
              onClick={testBasic}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#6c757d' : '#20c997',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '呼叫中...' : '✅ 基本驗證'}
            </button>
          </div>

          {error && (
            <div style={{
              padding: '10px',
              backgroundColor: '#f8d7da',
              color: '#721c24',
              border: '1px solid #f5c6cb',
              borderRadius: '4px',
              margin: '10px 0'
            }}>
              錯誤: {error}
            </div>
          )}

          {apiResponse && (
            <div style={{
              padding: '15px',
              backgroundColor: '#d4edda',
              color: '#155724',
              border: '1px solid #c3e6cb',
              borderRadius: '4px',
              margin: '10px 0'
            }}>
              <h4>API 回應:</h4>
              <pre style={{
                whiteSpace: 'pre-wrap',
                fontSize: '12px',
                maxHeight: '300px',
                overflow: 'auto'
              }}>
                {JSON.stringify(apiResponse, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default ProtectedPage;