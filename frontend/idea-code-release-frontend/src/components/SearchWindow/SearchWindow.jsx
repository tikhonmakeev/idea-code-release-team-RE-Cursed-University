import { useState } from 'react';
import Chat from '../Chat/Chat';
import Search from '../Search/Search';
import './style.css';

const SearchWindow = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (message) => {
    setMessages(prev => [...prev, { text: message, isUser: true }]);
    
    setIsLoading(true);
    
    try {
      const response = await fetch('#', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          role: role,
        }),
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        text: data.message, 
        isUser: false 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        text: 'Ошибка соединения с сервером', 
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='chat'>
      <div className='chat__container'>
        {messages.map((msg, index) => (
          <Chat 
            key={index} 
            text={msg.text} 
            isUser={msg.isUser} 
          />
        ))}
        {isLoading && (
          <Chat 
            text="AI думает..." 
            isUser={false} 
          />
        )}
      </div>
      <Search onSend={handleSend} disabled={isLoading} />
    </div>
  );
};

export default SearchWindow;