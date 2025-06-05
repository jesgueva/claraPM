import React from 'react';
import ReactMarkdown from 'react-markdown';

function Conversation({ conversation }) {
  return (
    <div id="conversation">
      {conversation.map((message, index) => (
        <div key={index} className={`message ${message.type}`}>
          <strong>{message.type === 'ai' ? 'Agent: ' : 'User: '}</strong>
          {message.type === 'ai' ? (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : (
            message.content
          )}
        </div>
      ))}
    </div>
  );
}

export default Conversation; 