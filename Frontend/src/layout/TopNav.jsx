import React from 'react';
import { Link } from 'react-router-dom';

export default function TopNav() {
  return (
    <nav className='p-5 sticky top-0 z-50 bg-gray-900 text-gray-100 flex justify-evenly'>
      <Link to='/'>Home</Link>
      <Link to='/login'>Login</Link>
      <Link to='/about'>About</Link>
    </nav>
  );
}
