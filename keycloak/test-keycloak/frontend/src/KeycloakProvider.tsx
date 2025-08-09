import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import keycloak from './keycloak';

interface KeycloakContextType {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
  login: () => void;
  logout: () => void;
  isLoading: boolean;
}

const KeycloakContext = createContext<KeycloakContextType | null>(null);

interface KeycloakProviderProps {
  children: ReactNode;
}

export const KeycloakProvider: React.FC<KeycloakProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    keycloak.init({
      onLoad: 'check-sso', // 初始化時檢查 SSO 狀態
      checkLoginIframe: false, // 關閉 iframe 檢查
      pkceMethod: 'S256', // 使用 PKCE 方法
    }).then((authenticated: boolean) => {
      setIsAuthenticated(authenticated);
      if (authenticated && keycloak.token) {
        setToken(keycloak.token);
        setUsername(keycloak.tokenParsed?.preferred_username || null);
      }
      setIsLoading(false);
    }).catch((error: any) => {
      console.error('Keycloak 初始化失敗:', error);
      setIsLoading(false);
    });

    keycloak.onTokenExpired = () => {
      keycloak.updateToken(30).then((refreshed: boolean) => {
        if (refreshed && keycloak.token) {
          setToken(keycloak.token);
        }
      }).catch(() => {
        console.warn('Token 更新失敗');
        logout();
      });
    };
  }, []);

  const login = () => {
    keycloak.login();
  };

  const logout = () => {
    keycloak.logout();
  };

  if (isLoading) {
    return <div>載入中...</div>;
  }

  return (
    <KeycloakContext.Provider value={{
      isAuthenticated,
      token,
      username,
      login,
      logout,
      isLoading
    }}>
      {children}
    </KeycloakContext.Provider>
  );
};

export const useKeycloak = (): KeycloakContextType => {
  const context = useContext(KeycloakContext);
  if (!context) {
    throw new Error('useKeycloak must be used within a KeycloakProvider');
  }
  return context;
};