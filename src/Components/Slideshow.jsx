import React, {  useEffect } from 'react';
import  {Slide}   from 'react-slideshow-image';
import 'react-slideshow-image/dist/styles.css';

const slideImages = [
  {
    url: require("../Images/main2.jpg"),
    
  },
  {
    url: require("../Images/main3.jpg"),
    
  },
  {
    url: require("../Images/main1.jpg"),
  },
];

const Slideshow = () => {
  const slideProperties = {
    duration: 8000,
    transitionDuration: window.innerWidth <= 768 ? 300 : 800,
    infinite: true,
    indicators: true,
    arrows: false,
  };

  return (
    <div className="slideshow-container">
      <Slide {...slideProperties}>
        {slideImages.map((imageData, index) => (
          <div key={index} className="each-slide-effect">
            <div style={{ 'backgroundImage': `url(${imageData.url})` }}>
              <AdditionalText caption={imageData.caption} />
            </div>
          </div>
        ))}
      </Slide>
    </div>
  );
};

const AdditionalText = ({ caption }) => {
  useEffect(() => {
    // Resetează animațiile pentru a le relua la fiecare schimbare de slide
    const textElement = document.querySelector('.additional-text');
    if (textElement) {
      textElement.style.animation = 'none';
      void textElement.offsetWidth;
      textElement.style.animation = null;
    }

    // Adaugă clasa pentru animația de tipewriter
    const typeInElement = document.querySelector('.additional-text');
    if (typeInElement) {
      typeInElement.classList.add('type-in-animation');
    }
  }, [caption]);

  return (
    <div className="additional-text">
      <p>{caption}</p>
    </div>
  );
};

export default Slideshow;
