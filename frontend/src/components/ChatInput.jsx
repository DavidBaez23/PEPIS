import React, { useState } from 'react';
import { Send } from 'lucide-react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="chat-input-container">
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Escribe tu pregunta aquí..."
          disabled={isLoading}
          autoFocus
        />
        <button 
          type="submit" 
          className="send-button" 
          disabled={!inputValue.trim() || isLoading}
          title="Enviar mensaje"
        >
          <Send size={18} />
        </button>
      </form>
      <div className="disclaimer">
        PEPIS puede cometer errores. Considera verificar la información importante en los documentos oficiales.
      </div>
    </div>
  );
};

export default ChatInput;
