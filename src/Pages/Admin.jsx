import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const Admin = () => {
  const [userName, setUserName] = useState('');
  const [selectedFunction, setSelectedFunction] = useState('dashboard');
  const [successMessage, setSuccessMessage] = useState('');
  const [hotels, setHotels] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);

  const [rooms, setRooms] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    stars: '',
    facilities: '',
    mainPhoto: null,
    hotelId: '',
    roomType: '',
    price: '',
    capacity: '',
    roomPhoto: null
  });
  

  useEffect(() => {
    fetch('https://26.14.218.21:5000/user', {
      method: 'GET',
      credentials: 'include',
    })
      .then(response => response.json())
      .then(data => {
        if (data && data.given_name) {
          setUserName(data.given_name);
        }
      })
      .catch(error => {
        console.error('Error fetching user info:', error);
      });

    fetchHotels();
  }, []);

  const fetchHotels = () => {
    fetch('https://26.14.218.21:5000/api/admin/hotels', {
      method: 'GET',
      credentials: 'include',
    })
      .then(response => response.json())
      .then(data => {
        setHotels(data);
      })
      .catch(error => {
        console.error('Error fetching hotels:', error);
      });
  };

  const fetchRooms = async (hotelId) => {
    try {
      const response = await fetch(`https://26.14.218.21:5000/api/admin/hotel_rooms?hotel_id=${hotelId}`, {
        method: 'GET',
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setRooms(data.rooms);
      } else {
        console.error('Error fetching hotel rooms:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  

  const handleAddHotel = async () => {
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('location', formData.location);
      formDataToSend.append('stars', formData.stars);
      formDataToSend.append('main_photo', formData.mainPhoto);
      formDataToSend.append('facilities', formData.facilities);
      const response = await fetch('https://26.14.218.21:5000/api/admin/add_hotel', {
        method: 'POST',
        credentials: 'include',
        body: formDataToSend
      });

      if (response.ok) {
        setSuccessMessage('Hotelul a fost înregistrat cu succes!');
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
        fetchHotels();
      } else {
        console.error('Eroare la adăugarea hotelului:', response.statusText);
      }
    } catch (error) {
      console.error('Eroare:', error);
    }
  };

  const handleDeleteHotel = async (hotelId) => {
    try {
      const response = await fetch('https://26.14.218.21:5000/api/admin/remove_hotel', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ hotel_id: hotelId })
      });

      if (response.ok) {
        setSuccessMessage('Hotelul a fost șters cu succes!');
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
        fetchHotels();
      } else {
        console.error('Eroare la ștergerea hotelului:', response.statusText);
      }
    } catch (error) {
      console.error('Eroare:', error);
    }
  };

  const handleUpdateHotel = async () => {
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('hotel_id', formData.hotelId);
      if (formData.name) formDataToSend.append('name', formData.name);
      if (formData.location) formDataToSend.append('location', formData.location);
      if (formData.stars) formDataToSend.append('stars', formData.stars);
      if (formData.mainPhoto) formDataToSend.append('main_photo', formData.mainPhoto);
      if (formData.facilities) formDataToSend.append('facilities', formData.facilities);

      const response = await fetch('https://26.14.218.21:5000/api/admin/edit_hotel', {
        method: 'POST',
        credentials: 'include',
        body: formDataToSend
      });

      if (response.ok) {
        setSuccessMessage('Hotelul a fost actualizat cu succes!');
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
        fetchHotels();
      } else {
        console.error('Eroare la actualizarea hotelului:', response.statusText);
      }
    } catch (error) {
      console.error('Eroare:', error);
    }
  };

  const handleAddRoom = async () => {
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('hotel_id', formData.hotelId);
      formDataToSend.append('room_type', formData.roomType);
      formDataToSend.append('price', formData.price);
      formDataToSend.append('capacity', formData.capacity);
      if (formData.roomPhoto) {
        formDataToSend.append('room_photo', formData.roomPhoto);
      }
      const response = await fetch('https://26.14.218.21:5000/api/admin/add_room', {
        method: 'POST',
        credentials: 'include',
        body: formDataToSend
      });

      if (response.ok) {
        setSuccessMessage('Camera a fost adăugată cu succes!');
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
        fetchRooms(formData.hotelId);
      } else {
        console.error('Eroare la adăugarea camerei:', response.statusText);
      }
    } catch (error) {
      console.error('Eroare:', error);
    }
  };
  const handleViewRooms = async (hotelId) => {
    try {
      const response = await fetch(`https://26.14.218.21:5000/api/admin/hotel_rooms?hotel_id=${hotelId}`, {
        method: 'GET',
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        console.log('Rooms data:', data); // Adăugăm console.log pentru a verifica conținutul datelor
        // Setează camerele hotelului în starea componentei pentru a le afișa în interfață
        setRooms(data);
        // Actualizează funcția selectată pentru a afișa lista de camere
        setSelectedFunction('viewRooms');
      } else {
        console.error('Error fetching hotel rooms:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (files) {
      setFormData({ ...formData, [name]: files[0] });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFunction === 'addHotel') {
      handleAddHotel();
    } else if (selectedFunction === 'updateHotel') {
      handleUpdateHotel();
    } else if (selectedFunction === 'addRoom') {
      handleAddRoom();
    }
  };


  

  const handleEditClick = (hotel) => {
    setFormData({
      name: hotel.name,
      location: hotel.location,
      stars: hotel.stars,
      facilities: hotel.facilities,
      mainPhoto: null,
      hotelId: hotel.id
    });
    setSelectedFunction('updateHotel');
  };

  const handleEditRoom = async (room) => {
    try {
      // Implementăm logica pentru editarea camerei
      setSelectedRoom(room);
      // Setează funcția selectată pentru a afișa formularul de editare a camerei
      setSelectedFunction('editRoom');
    } catch (error) {
      console.error('Eroare:', error);
    }
  };
  
  
  const handleDeleteRoom = async (roomId) => {
    try {
      const response = await fetch('https://26.14.218.21:5000/api/admin/remove_room', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ room_id: roomId })
      });
  
      if (response.ok) {
        setSuccessMessage('Camera a fost ștearsă cu succes!');
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
        
        // Actualizează lista de camere, filtrând camera ștearsă din state
        const updatedRooms = rooms.filter(room => room.id !== roomId);
        setRooms(updatedRooms);
      } else {
        console.error('Eroare la ștergerea camerei:', response.statusText);
      }
    } catch (error) {
      console.error('Eroare:', error);
    }
  };
  
  
  
  
  const renderRoomList = () => {
    return (
      <div>
        <h2>Lista Camerelor</h2>
        {rooms && rooms.length > 0 ? (
          <ul>
            {rooms.map(room => (
              <li key={room.id}>
                <p>Tip cameră: {room.room_type}</p>
                <p>Preț: {room.price}</p>
                <p>Capacitate: {room.capacity}</p>
                <img src={room.roomPhoto} alt="Camera" />
                <button onClick={() => handleEditRoom(room)}>Edit</button>
                <button onClick={() => handleDeleteRoom(room.id)}>Delete</button>
              

              </li>
            ))}
          </ul>
        ) : (
          <p>Nu există camere disponibile.</p>
        )}
      </div>
    );
  };
  
  
  
  
  

  const renderHotelList = () => {
    return (
      <div>
        <h2>Lista Hotelurilor</h2>
        {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
        <ul>
          {hotels.map(hotel => (
            <li key={hotel.id}>
              <p>Nume: {hotel.name}</p>
              <p>Locație: {hotel.location}</p>
              <p>Stele: {hotel.stars}</p>
              <p>Facilități: {hotel.facilities}</p>
              <button onClick={() => handleEditClick(hotel)}>Update</button>
              <button onClick={() => handleDeleteHotel(hotel.id)}>Delete</button>
              <button onClick={() => handleViewRooms(hotel.id)}>View Rooms</button>
              <button onClick={() => handleViewBookings(hotel.id)}>View Bookings</button>


              <button onClick={() => {
                setFormData({ ...formData, hotelId: hotel.id });
                setSelectedFunction('addRoom');
              }}>Add Room</button>
            </li>
          ))}
        </ul>
      </div>
    );
  };
  const handleViewBookings = async (hotelId) => {
    try {
      const response = await fetch(`https://26.14.218.21:5000/api/admin/hotel_bookings?hotel_id=${hotelId}`, {
        method: 'GET',
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        // Setează lista de rezervări în starea componentei
        setBookings(data);
        // Actualizează funcția selectată pentru a afișa lista de rezervări
        setSelectedFunction('viewBookings');
        console.log('Response from API:', data);

      } else {
        console.error('Error fetching hotel bookings:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  

  const renderContent = () => {
    switch (selectedFunction) {
      case 'addHotel':
      case 'updateHotel':
        return (
          <div>
            {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
            <h2>{selectedFunction === 'addHotel' ? 'Add Hotel Form' : 'Update Hotel Form'}</h2>
            <form onSubmit={handleSubmit} encType="multipart/form-data">
              <label>
                Nume hotel:
                <input type="text" name="name" value={formData.name} onChange={handleChange} />

              </label>
              <br />
              <label>
                Locație:
                <input type="text" name="location" value={formData.location} onChange={handleChange} />
              </label>
              <br />
              <label>
                Stele:
                <input type="text" name="stars" value={formData.stars} onChange={handleChange} />
              </label>
              <br />
              <label>
                Facilități:
                <input type="text" name="facilities" value={formData.facilities} onChange={handleChange} />
              </label>
              <br />
              <label>
                Imagine principală:
                <input type="file" name="mainPhoto" onChange={handleChange} />
              </label>
              <br />
              <button type="submit">{selectedFunction === 'addHotel' ? 'Adaugă Hotel' : 'Actualizează Hotel'}</button>
            </form>
          </div>
        );
      case 'viewHotels':
        return renderHotelList();
      case 'addRoom':
        return (
          <div>
            {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
            <h2>Add Room Form</h2>
            <form onSubmit={handleSubmit} encType="multipart/form-data">
              <label>
                Tip cameră:
                <input type="text" name="roomType" value={formData.roomType} onChange={handleChange} />
              </label>
              <br />
              <label>
                Preț:
                <input type="text" name="price" value={formData.price} onChange={handleChange} />
              </label>
              <br />
              <label>
                Capacitate:
                <input type="text" name="capacity" value={formData.capacity} onChange={handleChange} />
              </label>
              <br />
              <label>
                Fotografie cameră:
                <input type="file" name="roomPhoto" onChange={handleChange} />
              </label>
              <input type="hidden" name="hotelId" value={formData.hotelId} />
              <br />
              <button type="submit">Adaugă Cameră</button>
            </form>
          </div>
        );
        case 'viewBookings':
  return (
    <div>
      <h2>Lista Rezervărilor</h2>
      {bookings && bookings.length > 0 ? (
        <ul>
          {bookings.map(booking => (
            <li key={booking.id}>
              <p>Nume Client: {booking.user_name}</p>
              <p>Data Check-in: {new Date(booking.start_date).toLocaleDateString()}</p>
              <p>Data Check-out: {new Date(booking.end_date).toLocaleDateString()}</p>
              {/* Adăugați alte informații despre rezervare, după nevoie */}
            </li>
          ))}
        </ul>
      ) : (
        <p>Nu există rezervări disponibile pentru acest hotel.</p>
      )}
    </div>
  );


        case 'viewRooms':
  return renderRoomList();

  case 'editRoom':
  return (
    <div>
      {selectedRoom && (
        <div>
          <h2>Edit Room</h2>
          <form onSubmit={handleSubmit} encType="multipart/form-data">
            <label>
              Room Type:
              <input type="text" name="roomType" value={selectedRoom.roomType} onChange={handleChange} />
            </label>
            <br />
            <label>
              Price:
              <input type="text" name="price" value={selectedRoom.price} onChange={handleChange} />
            </label>
            <br />
            <label>
              Capacity:
              <input type="text" name="capacity" value={selectedRoom.capacity} onChange={handleChange} />
            </label>
            <br />
            <label>
              Room Photo:
              <input type="file" name="roomPhoto" onChange={handleChange} />
            </label>
            <input type="hidden" name="roomId" value={selectedRoom.id} />
            <br />
            <button type="submit">Update Room</button>
          </form>
        </div>
      )}
    </div>
  );

  
  


      default:
        return <div>Bine ati venit!</div>;
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-sidebar">
        <div className="admin-user-info">
          <h2>{userName}</h2>
          <Link to="/" className="home-link">
            <i className="fas fa-sign-out-alt"></i>
          </Link>
        </div>
        <nav className="admin-nav">
          <ul>
            <li onClick={() => setSelectedFunction('addHotel')}>Add Hotel</li>
            <li onClick={() => setSelectedFunction('viewHotels')}>View Hotels</li>
           
           
          </ul>
        </nav>
      </div>
      <div className="admin-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default Admin;

