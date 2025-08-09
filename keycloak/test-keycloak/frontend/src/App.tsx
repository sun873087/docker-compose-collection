import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { KeycloakProvider } from './KeycloakProvider';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import ProtectedPage from './pages/Protected';
import './App.css';

const App: React.FC = () => {
  return (
    <KeycloakProvider>
      <Router>
        <div className="App">
          <Navigation />
          <Switch>
            <Route exact path="/" component={Home} />
            <Route path="/protected" component={ProtectedPage} />
          </Switch>
        </div>
      </Router>
    </KeycloakProvider>
  );
};

export default App;