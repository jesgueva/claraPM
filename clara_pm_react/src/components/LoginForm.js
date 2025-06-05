import React, { useState, useEffect } from 'react';
import './LoginForm.css';

const LoginForm = ({ onLogin, error }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState('');
  const [loading, setLoading] = useState(false);

  // Update local error state when parent error changes
  useEffect(() => {
    if (error) {
      setLocalError(error);
    }
  }, [error]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setLocalError('Please enter both username and password');
      return;
    }
    
    setLocalError('');
    setLoading(true);
    
    try {
      const success = await onLogin(username, password);
      
      if (!success && !error) {
        setLocalError('Login failed. Please check your credentials.');
      }
    } catch (err) {
      setLocalError('Login failed. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-card">
        <h2>Login to Clara PM</h2>
        
        {localError && <div className="error-message">{localError}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              placeholder="Enter your username"
              autoComplete="username"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="login-help">
          <p>Default accounts for testing:</p>
          <ul>
            <li>Admin: username <strong>admin</strong>, password <strong>admin</strong></li>
            <li>User: username <strong>user</strong>, password <strong>user</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LoginForm; 