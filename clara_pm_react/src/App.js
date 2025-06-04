import React, { useState } from 'react';
import './App.css';
import InputForm from './components/InputForm';
import Conversation from './components/Conversation';

function App() {
  const [inputText, setInputText] = useState('');
  const [conversation, setConversation] = useState([]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await fetch('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_text: inputText })
    });
    const data = await response.json();

    if (Array.isArray(data.response.messages)) {
      setConversation(data.response.messages);
    } else {
      setConversation([{ type: 'ai', content: data.response.content }]);
    }
    setInputText(''); // Clear the input box after the request is sent
  };

  return (
    <div className="App">
      <h1>Project Manager Chat</h1>
      <Conversation conversation={conversation} />
      <InputForm inputText={inputText} setInputText={setInputText} handleSubmit={handleSubmit} />
    </div>
  );
}

export default App;
