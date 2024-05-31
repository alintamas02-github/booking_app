import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

const AccommodationSearch = () => {
  const [city, setCity] = useState('');
  const [cities, setCities] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [num_people, setPersons] = useState(1);

  useEffect(() => {
    const fetchCities = async () => {
      try {
        const response = await fetch('https://26.14.218.21:5000/api/cities');
        if (!response.ok) {
          console.error('HTTP Status Code:', response.status);
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setCities(data);
      } catch (error) {
        console.error('Failed to fetch cities:', error);
      }
    };

    fetchCities();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    // Verificați dacă orașul este selectat
    if (!city) {
      console.error('Orașul nu a fost selectat.');
      return; // Întrerupeți procesarea dacă orașul nu este selectat
    }
  
    const queryParams = new URLSearchParams({
      city,
      startDate,
      endDate,
      num_people
    }).toString();
  
    // Construiește URL-ul cu query params
    const url = `https://26.14.218.21:5000/api/search_hotels?${queryParams}`;

    // Redirecționează către pagina HotelSearchResults
    window.location.href = `/hotelsearchresult?${queryParams}`;
  };
  
  const handleCityChange = (e) => {
    setCity(e.target.value);
  };

  const handleStartDateChange = (e) => {
    setStartDate(e.target.value);
    
    // Reset end date if it's before the new start date
    if (endDate && e.target.value > endDate) {
      setEndDate('');
    }
  };

  const handleEndDateChange = (e) => {
    setEndDate(e.target.value);
  };

  const handleAdultsChange = (e) => {
    setPersons(e.target.value);
  };

  return (
    <div className="accommodation-search-overlay">
      <form onSubmit={handleSubmit}>
        <div className="search-bar">
          {/* Replace the input with a select dropdown */}
          <select className="input-field" value={city} onChange={handleCityChange}>
            <option value="">Selectează orașul</option>
            {cities.map((cityObj, index) => (
              <option key={index} value={cityObj.location}>
                {cityObj.location}
              </option>
            ))}
          </select>
          <button type="submit" className="search-button"><FontAwesomeIcon icon={faSearch} /></button>
        </div>

        <div className="date-picker">
          <label>Data inceput:</label>
          <input type="date" className="input-field" value={startDate} onChange={handleStartDateChange} />
        </div>
        <div className="date-picker">
          <label>Data sfarsit:</label>
          <input type="date" className="input-field" value={endDate} onChange={handleEndDateChange} min={startDate} />
        </div>
        <div className="guests">
          <label>Persoane:</label>
          <input type="number" className="input-field" value={num_people} onChange={handleAdultsChange} />
        </div>
      </form>
    </div>
  );
};

export default AccommodationSearch;
