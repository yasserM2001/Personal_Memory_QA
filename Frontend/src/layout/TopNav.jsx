import React from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';

export default function TopNav() {

  const {user , logout} = useContext(AuthContext);  
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/'); 
  };
  
  return (
    <nav className='p-5 sticky top-0 z-50 bg-gray-900 text-gray-100 flex justify-evenly'>
      <Link to='/'>Home</Link>
      {user ?(
        <>
          <button onClick={handleLogout}>Logout</button>
          <Link to="/init">Init</Link>
        </>
        ):(
          <Link to='/login'>Login</Link>
        )
      }
      <Link to='/about'>About</Link>
    </nav>
  );
}
