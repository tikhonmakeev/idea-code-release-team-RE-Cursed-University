import { useState } from 'react';
import React from 'react';
import './style.css';

const Search = ({ onSend, placeholder }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
        onSend(message);
        setMessage('');
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64String = e.target.result;
        onSend(base64String);
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePressInput = () => {
    const input = document.getElementById('files');
    input.click();
  };

  return (
    <form className='search' method='POST' onSubmit={handleSubmit}>
      <input type="text" onChange={(e) => setMessage(e.target.value)} placeholder={placeholder}  value={message}className='search__input'/>
      <button type='submit' className='search__btn'></button>
      <button type='button' className='search__btn search__upload' onClick={handlePressInput}></button>
      <input type="file" className='search__files' id='files' multiple/>
    </form>
  );
};

export default Search;