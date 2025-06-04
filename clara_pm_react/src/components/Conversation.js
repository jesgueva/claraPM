import React from 'react';

function Conversation({ conversation }) {
  return (
    <div id="conversation">
      {conversation.map((message, index) => (
        <div key={index} className={`message ${message.type}`}>
          {message.type === 'ai' ? 'Agent: ' : 'User: '}{message.content}
        </div>
      ))}
    </div>
  );
}

export default Conversation; 