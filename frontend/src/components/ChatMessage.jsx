import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatMessage.css';
import logo from '../assets/logo.png';

const ChatMessage = ({ message, isBot, isLoading }) => {
  return (
    <div className={`message-wrapper ${isBot ? 'bot' : 'user'}`}>
      {isBot && (
        <div className="message-avatar">
          <img src={logo} alt="PEPIS Avatar" onError={(e) => { e.target.style.display = 'none'; }} />
        </div>
      )}

      <div className="message-bubble">
        {isLoading ? (
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        ) : isBot ? (
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message}
            </ReactMarkdown>
          </div>
        ) : (
          <div>{message}</div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
