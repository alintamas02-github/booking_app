import React, { useEffect, useState } from 'react';
import Navbar from '../Components/Navbar';
import Slideshow from '../Components/Slideshow';
import Socialbar from '../Components/Socialbar';
import AccommodationSearch from '../Components/AccomodationSearch';



function HomePage() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Verifică dacă dispozitivul curent este un telefon mobil
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 768); // Poți ajusta 768 în funcție de nevoile tale
    };

    // Verifică la încărcarea paginii și la redimensionare
    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);

    // Cleanup la dezabonare
    return () => {
      window.removeEventListener('resize', checkIsMobile);
    };
  }, []);

  return (
    <div>
      <Slideshow />
      <Navbar enableScrollEffect={true} />
      {!isMobile && <Socialbar />} {/* Afișează bara socială doar dacă nu este un telefon mobil */}
      <AccommodationSearch />
    </div>
  );
}

export default HomePage;
