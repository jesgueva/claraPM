import React, { useState, useEffect } from 'react';
import './App.css';
import InputForm from './components/InputForm';
import Conversation from './components/Conversation';
import LoginForm from './components/LoginForm';

// Configure API base URL 
const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [inputText, setInputText] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState('');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState(null);

  // Check if user is already logged in (token in localStorage)
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    const storedSessionId = localStorage.getItem('sessionId');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      
      if (storedSessionId) {
        setSessionId(storedSessionId);
        // Fetch the existing conversation if there's a session ID
        fetchSession(storedSessionId, storedToken);
      }
    }
    
    setLoading(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);  // fetchSession is defined after this hook, so we're disabling the lint warning

  // Fetch an existing session's messages
  const fetchSession = async (sessionId, authToken) => {
    try {
      setError('');
      const response = await fetch(`${API_BASE_URL}/intake/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${authToken || token}`
        }
      });
      
      if (!response.ok) {
        // If session not found, clear session ID
        if (response.status === 404) {
          localStorage.removeItem('sessionId');
          setSessionId(null);
          return;
        }
        
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch session');
      }
      
      const data = await response.json();
      if (data.messages && Array.isArray(data.messages)) {
        setConversation(data.messages);
        console.log('Loaded existing session:', sessionId, 'with', data.messages.length, 'messages');
      }
    } catch (error) {
      console.error('Error fetching session:', error);
      setError(error.message);
    }
  };

  const handleLogin = async (username, password) => {
    try {
      setError('');
      // Create form data for login
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch(`${API_BASE_URL}/token`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      
      // Save token and set authentication state
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      
      // Get user information
      const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
      }
      
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      setError(error.message);
      return false;
    }
  };

  const handleLogout = () => {
    // Clear token and user info
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionId');
    setToken('');
    setUser(null);
    setIsAuthenticated(false);
    setConversation([]);
    setSessionId(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!isAuthenticated) {
      alert('Please log in first!');
      return;
    }
    
    try {
      setError('');
      // Store the user message immediately to show in UI
      const userMessage = { type: 'user', content: inputText };
      setConversation(prev => [...prev, userMessage]);
      
      // Create request payload, including session ID if it exists
      const payload = { 
        input_text: inputText,
      };
      
      if (sessionId) {
        payload.session_id = sessionId;
      }
      
      console.log('Sending request with payload:', payload);
      
      const response = await fetch(`${API_BASE_URL}/intake/query`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Request failed');
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      
      // Store the session ID for future use
      if (data.session_id) {
        setSessionId(data.session_id);
        localStorage.setItem('sessionId', data.session_id);
      }
      
      if (Array.isArray(data.messages) && data.messages.length > 0) {
        setConversation(data.messages);
      } else if (data.response) {
        // If no messages array but there's a response, add just the AI response
        // (keeping the user message that was already added)
        setConversation(prev => {
          // Find if the user's message is already in the conversation
          const hasUserMessage = prev.some(
            msg => msg.type === 'user' && msg.content === inputText
          );
          
          if (hasUserMessage) {
            return [...prev, { type: 'ai', content: data.response }];
          } else {
            return [...prev, userMessage, { type: 'ai', content: data.response }];
          }
        });
      }
      
      setInputText(''); // Clear the input box after the request is sent
    } catch (error) {
      console.error('Error sending message:', error);
      setError(error.message);
    }
  };

  const startNewConversation = () => {
    localStorage.removeItem('sessionId');
    setSessionId(null);
    setConversation([]);
  };

  if (loading) {
    return <div className="App">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Clara Project Manager</h1>
        {isAuthenticated && user && (
          <div className="user-info">
            <span>Welcome, {user.full_name || user.username}</span>
            <div className="header-buttons">
              <button onClick={startNewConversation} className="new-chat-btn">New Chat</button>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </div>
          </div>
        )}
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}

      {isAuthenticated ? (
        <div className="chat-container">
          <Conversation 
            conversation={conversation} 
            sessionId={sessionId}
          />
          <InputForm 
            inputText={inputText} 
            setInputText={setInputText} 
            handleSubmit={handleSubmit} 
          />
        </div>
      ) : (
        <LoginForm onLogin={handleLogin} error={error} />
      )}
    </div>
  );
}

export default App;
