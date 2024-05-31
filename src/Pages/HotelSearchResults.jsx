import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from '../Components/Navbar';
import Slideshow from '../Components/Slideshow';
import Socialbar from '../Components/Socialbar';
 
const fetchInitialHotels = async (city, startDate, endDate, numPeople, setLoading, setHotels, setLoadedHotels) => {
  setLoading(true);
  const apiUrl = `https://26.14.218.21:5000/api/search_hotels?city=${city}&startDate=${startDate}&endDate=${endDate}&num_people=${numPeople}`;
  try {
    const response = await fetch(apiUrl, {credentials: "include"});
    if (!response.ok) {
      console.error('HTTP Status Code:', response.status);
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    setHotels(data);
    setLoading(false);
    setLoadedHotels(10);
  } catch (error) {
    console.error('Failed to fetch hotel results:', error);
    // Handle error appropriately
    setLoading(false);
  }
};
 
const HotelSearchResults = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const city = searchParams.get('city');
  const startDate = searchParams.get('startDate');
  const endDate = searchParams.get('endDate');
  const numPeople = searchParams.get('num_people');
  const [hotels, setHotels] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadedHotels, setLoadedHotels] = useState(0);
  const containerRef = useRef(null);
  const [reservationStatus, setReservationStatus] = useState(null);
  const [isReserving, setIsReserving] = useState(false); // Indicator pentru a arăta că se face o rezervare
 
  const loadMoreHotels = async () => {
    setLoading(true);
    const start = loadedHotels;
    const end = loadedHotels + 10;
    const apiUrl = `http://26.14.218.21:5000/api/search_hotels?city=${city}&startDate=${startDate}&endDate=${endDate}&num_people=${numPeople}`;
    try {
      const response = await fetch(apiUrl, {credentials: "include"});
      if (!response.ok) {
        console.error('HTTP Status Code:', response.status);
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setHotels([...hotels, ...data]);
      setLoading(false);
      setLoadedHotels(end);
    } catch (error) {
      console.error('Failed to fetch hotel results:', error);
      setError('Failed to fetch hotel results.');
      setLoading(false);
    }
  };
 
  useEffect(() => {
    fetchInitialHotels(city, startDate, endDate, numPeople, setLoading, setHotels, setLoadedHotels);
  }, [city, startDate, endDate, numPeople]);
 
  useEffect(() => {
    const handleScroll = () => {
      const container = containerRef.current;
      if (container) {
        const scrollBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
        if (scrollBottom === 0 && !loading) {
          loadMoreHotels();
        }
      }
    };
 
    window.addEventListener('scroll', handleScroll);
 
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [loading, loadMoreHotels]);
 
 
  const handleReservation = async (roomId) => {
  setIsReserving(true); // Setează starea pentru a afișa "Loading" când utilizatorul apasă butonul de rezervare
 
  try {
    // Actualizează starea generală de încărcare pentru a afișa "Loading"
    setLoading(true);
 
    const response = await fetch('https://26.14.218.21:5000/api/book_room', {
      credentials: "include",
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room_id: roomId
      })
    });
 
    if (!response.ok) {
      console.error(response);
      throw new Error('Network response was not ok');
    }
 
    // Actualizează starea listei de hoteluri după realizarea rezervării
    await fetchInitialHotels(city, startDate, endDate, numPeople, setLoading, setHotels, setLoadedHotels);
    setReservationStatus('Rezervat cu succes');
  } catch (error) {
    console.error('Failed to book room:', error);
    setReservationStatus('Rezervarea a eșuat');
  } finally {
    // După ce s-a finalizat procesul de rezervare, oprește starea pentru a afișa "Loading"
    setIsReserving(false);
    setLoading(false);
  }
};
 
 
  return (
    <div>
      <Slideshow />
      <Navbar enableScrollEffect={true} />
      <div className="hotel-search-overlay" ref={containerRef}>
        <div className="hotel-search-results-container">
          {error ? (
            <p>{error}</p>
          ) : reservationStatus ? (
            <p>{reservationStatus}</p>
          ) : (
            <div className="hotel-list">
              {hotels.map((hotel) => (
                <div key={hotel.id} className="hotel-card">
                  <img src={`https://26.14.218.21:5000/api/hotel_photo/${hotel.hotel_id}`} alt={hotel.name} />
                  <div className="hotel-details">
                    <h3>{hotel.name}</h3>
                    <p className="hotel-price">Preț: {hotel.price} RON</p>
                    <p className="hotel-facilities">Facilități: {hotel.facilities.join(', ')}</p>
                    <p>Locație: {hotel.location}</p>
                  </div>
                  <button className="reservation-button" onClick={() => handleReservation(hotel.room_id)}>Rezervă</button>
                </div>
              ))}
              {loading && <p>Loading...</p>}
              {isReserving && <p>Se face rezervarea...</p>} {/* Afișează indicatorul de încărcare */}
            </div>
          )}
        </div>
      </div>
      <Socialbar />
    </div>
  );
};
 
export default HotelSearchResults;