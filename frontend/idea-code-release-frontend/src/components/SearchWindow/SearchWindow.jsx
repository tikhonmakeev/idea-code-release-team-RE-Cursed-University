import { useState, useEffect, useCallback, useRef } from 'react';
import Chat from '../Chat/Chat';
import Search from '../Search/Search';
import './style.css';

const SearchWindow = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [authStatus, setAuthStatus] = useState('unauthenticated'); // 'checking' | 'authenticated' | 'unauthenticated'
  const messagesEndRef = useRef(null); 
  const apiUrl = import.meta.env.VITE_API_URL;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'nearest'
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Проверка валидности credentials
  const checkAuth = useCallback(async () => {
    const credentials = localStorage.getItem('basicAuthCredentials');
    if (!credentials) {
      setAuthStatus('unauthenticated');
      return false;
    } else {
      setAuthStatus('authenticated');
    }
  }, [apiUrl]);

  const fetchHistory = useCallback(async () => {
    if (authStatus !== 'authenticated') return;
    
    setIsLoading(true);
    try {
      const credentials = localStorage.getItem('basicAuthCredentials');
      const response = await fetch(`${apiUrl}/messages/history`, {
        method: 'GET',
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Ошибка загрузки истории');
      
      const data = await response.json();
      setMessages(data.map(item => ({
        text: item.body,
        isUser: item.role === 'user'
      })));
    } catch (error) {
      console.error('Ошибка:', error);
      setMessages([{
        text: 'Не удалось загрузить историю сообщений',
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, authStatus]);

  useEffect(() => {
    const init = async () => {
      await checkAuth();
      if (authStatus === 'authenticated') {
        await fetchHistory();
      }
    };
    init();
  }, [checkAuth, fetchHistory, authStatus]);

  const handleSend = async (message) => {
    if (!message.trim() || authStatus !== 'authenticated') return;

    setMessages(prev => [...prev, { text: message, isUser: true }]);
    setIsLoading(true);
    
    try {
      const credentials = localStorage.getItem('basicAuthCredentials');
      const response = await fetch(`${apiUrl}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ body: message }),
      });

      if (!response.ok) throw new Error('Ошибка отправки');
      
      const data = await response.json();
      setMessages(prev => [...prev, { 
        text: data.body, 
        isUser: false 
      }]);
    } catch (error) {
      console.error('Ошибка:', error);
      setMessages(prev => [...prev, { 
        text: 'Ошибка соединения с сервером', 
        isUser: false 
      }]);
      
      // При ошибке 401 (Unauthorized) разлогиниваем
      if (error.message.includes('401')) {
        localStorage.removeItem('basicAuthCredentials');
        setAuthStatus('unauthenticated');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='chat'>
      <div className='chat__container'>
        {authStatus === 'unauthenticated' ? (
          <Chat 
            text="Для доступа к чату войдите в систему" 
            isUser={false} 
            isSystemMessage={true}
          />
        ) : (
          <>
            <Chat 
              text="Вы успешно авторизованы" 
              isUser={false} 
              isSystemMessage={true} 
            />
            {messages.map((msg, index) => (
              <Chat 
                key={`${index}-${Date.now()}`} 
                text={msg.text} 
                isUser={msg.isUser} 
              />
            ))}
          </>
        )}
        
        {isLoading && (
          <Chat text="AI думает..." isUser={false} />
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <Search 
        onSend={handleSend} 
        disabled={isLoading || authStatus !== 'authenticated'}
        placeholder={authStatus !== 'authenticated' ? 'Авторизуйтесь для отправки' : 'Введите сообщение...'}
      />
    </div>
  );
};

export default SearchWindow;