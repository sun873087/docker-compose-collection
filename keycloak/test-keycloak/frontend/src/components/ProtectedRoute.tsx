import React, { ReactNode } from 'react';
import { useKeycloak } from '../KeycloakProvider';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, login } = useKeycloak();

  if (!isAuthenticated) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>需要登入</h2>
        <p>您需要登入才能訪問此頁面</p>
        <button 
          onClick={login}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          登入
        </button>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;