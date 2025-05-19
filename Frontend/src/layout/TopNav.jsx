import React from 'react';
import { useEffect } from 'react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const BASE_URL = "http://localhost:5000";

export default function TopNav() {

  const [isLoggedin , setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(()=>{
    const token = localStorage.getItem('accessToken');
    setIsLoggedIn(!!token);
  },[]);

  const handleLogOut = async () => {
    localStorage.clear();
    setIsLoggedIn(false);
    navigate('/');
  };
  
  return (
    <nav className='p-5 sticky top-0 z-50 bg-gray-900 text-gray-100 flex justify-evenly'>
      <Link to='/'>Home</Link>
      {
        isLoggedin?(
          <button onClick={handleLogOut}>Logout</button>
        ):(
          <Link to='/login'>Login</Link>
        )
      }
      {isLoggedin && <Link to="/init">Init</Link>}
      <Link to='/about'>About</Link>
    </nav>
  );
}
