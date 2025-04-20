import React from 'react';
import './style.css';

const ChatMessage = ({ text, isUser }) => {
  return (
    <div className={`chat__message ${isUser ? 'chat__user' : 'chat__ai'}`}>
      <div className='chat__text'>{text}</div>
    </div>
  );
};

export default ChatMessage;