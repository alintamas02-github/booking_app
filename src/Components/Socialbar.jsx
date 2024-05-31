import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInstagram, faFacebook, faPinterest, faGithub  } from '@fortawesome/free-brands-svg-icons';

const SocialBar = () => {
  return (
    <div className="social-bar">
      <a href="https://instagram.com" target="_blank" rel="noopener noreferrer">
      <FontAwesomeIcon icon={faInstagram} />
      </a>
      <a href="https://facebook.com" target="_blank" rel="noopener noreferrer">
        <FontAwesomeIcon icon={faFacebook} />
      </a>
      <a href="https://pinterest.com" target="_blank" rel="noopener noreferrer">
        <FontAwesomeIcon icon={faPinterest} />
      </a>
      <a href="https://github.com" target="_blank" rel="noopener noreferrer">
        <FontAwesomeIcon icon={faGithub} />
      </a>
    </div>
  );
};

export default SocialBar;
