import React from 'react';
import './style.css';
import logo from '../../assets/logo.svg';

const Header = () => {
  return (
    <header className='header'>
      <a href="#" className='header__link'>
        <img src={logo} alt="Логотип" className='header__img'/>
      </a>
    </header>
  );
};

export default Header;
