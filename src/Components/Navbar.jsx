import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import SocialBar from '../Components/Socialbar';
import { GoogleLogin } from '@react-oauth/google';
import {jwtDecode} from 'jwt-decode';

function Navbar({ enableScrollEffect }) {
  const [scrolling, setScrolling] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [navbarColor, setNavbarColor] = useState('transparent');
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    const handleScroll = () => {
      if (enableScrollEffect && window.scrollY > 500) {
        setScrolling(true);
      } else {
        setScrolling(false);
      }
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [enableScrollEffect]);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);

    if (!menuOpen) {
      document.body.classList.add('open-menu');
      setNavbarColor('#000000');
    } else {
      document.body.classList.remove('open-menu');
      setNavbarColor('transparent');
    }
  };

  const navbarStyle = {
    backgroundColor: enableScrollEffect && scrolling ? '#000000' : navbarColor,
    transition: 'background-color 0.3s ease',
    zIndex: '100',
    position: 'fixed',
    width: '100%',
    fontFamily: "'Indie Flower', cursive",
  };

  if (!enableScrollEffect) {
    navbarStyle.backgroundColor = '#000000';
  }

  const handleLoginSuccess = (response) => {
    const googleCredentials = jwtDecode(response.credential);
    fetch('https://26.14.218.21:5000/login', {
      credentials: 'include',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        credentials: googleCredentials
      })
    }).then(() => {
      window.location.reload();
    });
  };

  const handleLoginFailure = (response) => {
    console.log('Login Failed:', response);
  };

  const handleLogout = () => {
    fetch('https://26.14.218.21:5000/logout', {
      credentials: 'include',
      method: 'POST'
    }).then(() => {
      window.location = 'http://localhost:3000';
    });
  };

  useEffect(() => {
    fetch('https://26.14.218.21:5000/user', {
      method: 'GET',
      credentials: 'include',
    })
      .then(response => response.json())
      .then(data => {
        if (Object.keys(data).length === 0) {
          setUserInfo(null);
        } else {
          setUserInfo(data);
        }
      })
      .catch(error => {
        console.error('Error fetching user info:', error);
        setUserInfo(null);
      });
  }, []);

  return (
    <nav className={`navbar ${menuOpen ? 'open' : ''}`} style={navbarStyle}>
      <Link to="/">
        <div className="logo">
          <h1 style={{ color: '#ffffff', fontSize: '30px', fontWeight: 'bold', marginLeft: '50px' }}>HAVENWISH</h1>
        </div>
      </Link>
      <ul className={`nav-links ${menuOpen ? 'open' : ''}`}>
        {userInfo ? (
          <>
            {userInfo.role === 'admin' && (
              <li>
                <Link to="/admin">Panou de control</Link>
              </li>
            )}
            <li>
              <Link to="/profile">My Account</Link>
              <button onClick={handleLogout}>Logout</button>
            </li>
          </>
        ) : (
          <li>
            <GoogleLogin onSuccess={handleLoginSuccess} onError={handleLoginFailure} />
          </li>
        )}
        <li className={`last-item ${window.innerWidth <= 768 ? 'mobile-margin' : ''}`}>
          {menuOpen && window.innerWidth <= 768 && <div className="white-line" />}
        </li>
        {menuOpen && window.innerWidth <= 768 && (
          <li className={`social-bar-mobile ${window.innerWidth <= 768 ? 'last' : ''}`}>
            <SocialBar />
          </li>
        )}
      </ul>
      <div className="menu-icon" onClick={toggleMenu}>
        =
      </div>
    </nav>
  );
}

export default Navbar;
