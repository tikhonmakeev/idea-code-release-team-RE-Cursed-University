import { useState, useEffect, useCallback, useRef } from 'react';
import Chat from '../Chat/Chat';
import Search from '../Search/Search';
import './style.css';

const SearchWindow = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const credentials = localStorage.getItem('basicAuthCredentials');
  const messagesEndRef = useRef(null); 

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'nearest'
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch('http://192.168.0.139:8001/api/v1/messages/history', {
        method: 'GET',
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка загрузки истории');
      }

      const data = await response.json();
      
      // Преобразуем данные API в нужный формат
      const formattedMessages = data.map(item => ({
        text: item.body,
        isUser: item.role === 'user'
      }));

      setMessages(formattedMessages);
    } catch (error) {
      console.error('Ошибка загрузки истории:', error);
      setMessages(prev => [...prev, {
        text: 'Не удалось загрузить историю сообщений',
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [credentials]);

  useEffect(() => {
    // Добавляем проверку на наличие credentials
    if (credentials) {
      fetchHistory();
    }
  }, [fetchHistory, credentials]);

  const handleSend = async (message) => {
    setMessages(prev => [...prev, { text: message, isUser: true }]);
    
    setIsLoading(true);
    
    try {
      const response = await fetch('http://192.168.0.139:8001/api/v1/messages', {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          body: message,
        }),
      });
      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        text: data.body, 
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
        <div ref={messagesEndRef} />
      </div>
      <Search onSend={handleSend} disabled={isLoading} />
    </div>
  );
};

export default SearchWindow;