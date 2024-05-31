import './App.css';
import {  Route ,Routes, BrowserRouter} from "react-router-dom";
import React from 'react';
import Home from './Pages/Home';
import Admin from './Pages/Admin';
//import SearchResultsPage from './Pages/SearchResultsPage';



import 'react-slideshow-image/dist/styles.css';
import HotelSearchResults from './Pages/HotelSearchResults';
import UserProfile from './Pages/UserProfile';

function App() {
  return (
    
      <BrowserRouter>
      
      <Routes>
        <Route index element={<Home />} />
        <Route path="/hotelsearchresult" element={<HotelSearchResults />} />
        <Route path="/profile" element={<UserProfile/>} />
        <Route path='/admin' element={<Admin/>} />

        </Routes>
     </BrowserRouter>
    
  );
}

export default App;
