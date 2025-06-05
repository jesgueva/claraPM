import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

function Conversation({ conversation, sessionId }) {
  const conversationEndRef = useRef(null);

  // Auto-scroll to bottom when conversation updates
  useEffect(() => {
    if (conversationEndRef.current) {
      conversationEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation]);

  if (!conversation || conversation.length === 0) {
    return (
      <div className="conversation empty-conversation">
        <div className="welcome-message">
          <h3>Welcome to Clara Project Manager</h3>
          <p>Start a conversation with the AI assistant to manage your projects.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-container">
      {sessionId && (
        <div className="session-info">
          Session: {sessionId}
        </div>
      )}
      <div className="conversation">
        {conversation.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <strong>{message.type === 'ai' ? 'Clara: ' : 'You: '}</strong>
            {message.type === 'ai' ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : (
              message.content
            )}
          </div>
        ))}
        <div ref={conversationEndRef} />
      </div>
    </div>
  );
}

export default Conversation; 