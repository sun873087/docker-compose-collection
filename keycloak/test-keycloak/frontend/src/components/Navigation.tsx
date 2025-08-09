import React from 'react';
import { Link } from 'react-router-dom';
import { useKeycloak } from '../KeycloakProvider';

const Navigation: React.FC = () => {
  const { isAuthenticated, username, login, logout } = useKeycloak();

  return (
    <nav style={{
      padding: '10px 20px',
      backgroundColor: '#f8f9fa',
      borderBottom: '1px solid #dee2e6',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div>
        <Link to="/" style={{ marginRight: '20px', textDecoration: 'none' }}>首頁</Link>
        <Link to="/protected" style={{ textDecoration: 'none' }}>受保護頁面</Link>
      </div>
      
      <div>
        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>歡迎, {username}!</span>
            <button 
              onClick={logout}
              style={{
                padding: '5px 10px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              登出
            </button>
          </div>
        ) : (
          <button 
            onClick={login}
            style={{
              padding: '5px 10px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            登入
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navigation;