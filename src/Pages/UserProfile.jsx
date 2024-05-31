import React, { useEffect, useState } from 'react';
import Slideshow from '../Components/Slideshow';
import Navbar from '../Components/Navbar';
import Socialbar from '../Components/Socialbar';

const UserProfile = () => {
  const [userData, setUserData] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch(`https://26.14.218.21:5000/user`, {
          credentials: "include",
        });
        const data = await response.json();
        setUserData({
          numeUtilizator: data.given_name,
          name: data.name,
          picture: data.picture,
        });
        // Fetch user bookings after fetching user data
        fetchUserBookings();
      } catch (error) {
        console.error('Eroare la aducerea datelor utilizatorului:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const fetchUserBookings = async () => {
    try {
      // Fetch user bookings from server
      const response = await fetch('https://26.14.218.21:5000/api/user_bookings', { credentials: 'include' });
      if (!response.ok) {
        console.error('HTTP Status Code:', response.status);
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log('Bookings:', data); // Log the bookings data
      setBookings(data);
    } catch (error) {
      console.error('Failed to fetch user bookings:', error);
    }
  };

  const handleReservation = async (roomId) => {
    try {
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
        console.error('HTTP Status Code:', response.status);
        throw new Error('Network response was not ok');
      }
      // Refresh user bookings after making reservation
      fetchUserBookings();
    } catch (error) {
      console.error('Failed to book room:', error);
    }
  };

  const handleCancelBooking = async (bookingId) => {
    try {
      const response = await fetch('https://26.14.218.21:5000/api/cancel_booking', {
        credentials: "include",
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          booking_id: bookingId
        })
      });
      if (!response.ok) {
        console.error('HTTP Status Code:', response.status);
        throw new Error('Network response was not ok');
      }
      // Refresh user bookings after cancelling
      fetchUserBookings();
    } catch (error) {
      console.error('Failed to cancel booking:', error);
    }
  };

  if (loading) {
    return <div>Se încarcă...</div>;
  }

  if (!userData) {
    return <div>Failed to load user data</div>;
  }

  return (
    <div className="user-profile-container">
      <Slideshow />
      <Navbar enableScrollEffect={true} />
      <Socialbar />
      <div className="user-data">
        <div className="user-info">
          <h1>Salut, {userData.numeUtilizator}</h1>
          <p>{userData.name}</p>
        </div>
        {userData.picture && (
          <img
            src={userData.picture}
            alt="Profil"
            className="profile-picture"
          />
        )}
        <div className="user-bookings">
          <h2>Rezervările mele</h2>
          {bookings.length > 0 ? (
            <ul>
              {bookings.map((booking) => (
                <li key={booking.id}>
                  <p><strong>Hotel:</strong> {booking.hotel_name}</p>
                  <p><strong>Start Date:</strong> {booking.start_date}</p>
                  <p><strong>End Date:</strong> {booking.end_date}</p>
                  <p><strong>People:</strong> {booking.people}</p>
                  <button onClick={() => handleCancelBooking(booking.id)}>Anulează rezervarea</button>
                </li>
              ))}
            </ul>
          ) : (
            <p>Nu ai nicio rezervare momentan.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
