import React from 'react';

function InputForm({ inputText, setInputText, handleSubmit }) {
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="Enter your query"
        required
      />
      <button type="submit">Send</button>
    </form>
  );
}

export default InputForm; 