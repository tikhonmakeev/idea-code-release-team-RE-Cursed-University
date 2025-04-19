import { useState } from 'react';
import React from 'react';
import './style.css';

const Search = ({ onSend }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
        onSend(message);
        setMessage('');
    }
  };
  return (
    <form className='search' method='POST' onSubmit={handleSubmit}>
      <input type="text" placeholder='Поиск' onChange={(e) => setMessage(e.target.value)} value={message}className='search__input'/>
      <button type='submit' className='search__btn'></button>
    </form>
  );
};

export default Search;