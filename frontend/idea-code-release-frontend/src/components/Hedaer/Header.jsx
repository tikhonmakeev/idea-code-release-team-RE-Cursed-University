import React from 'react';
import { useState } from 'react';
import './style.css';
import logo from '../../assets/logo.svg';
import AuthPopup from '../AuthPopup/AuthPopup';

const Header = () => {
  const [showAuthPopup, setShowAuthPopup] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem('basicAuthCredentials')
  );

  const handleAuthSuccess = (credentials) => {
    localStorage.setItem('basicAuthCredentials', credentials);
    setIsAuthenticated(true);
  };

  return (
    <header className='header'>
      <a href="#" className='header__link'>
        <img src={logo} alt="Логотип" className='header__img'/>
      </a>
      {isAuthenticated ? (
            <img src='../assets/user.svg' alt="Аватар" className='header__img' />
          ) : (
            <button className='header__btn' onClick={() => setShowAuthPopup(true)}></button>
          )}

      {showAuthPopup && (
        <AuthPopup 
          onClose={() => setShowAuthPopup(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}

    </header>
  );
};

export default Header;
