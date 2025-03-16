import React from 'react'
import { Link } from 'react-router-dom'
import { useState } from 'react';
import Login from '../components/auth/Login';
import About from '../pages/About';
import Home from '../pages/Home';

export default function TopNav() {

  const [form, setForm] = useState("");

  return (
    <div className='relative'>
    <nav className='p-5 sticky top-0  bg-gray-900 text-gray-100 flex justify-evenly'>
        <Link to='/'onClick={() => setForm(<Home />)} >Home</Link>
        <Link to='/login' onClick={() => setForm(<Login />)} >Login</Link>
        <Link to='/about'onClick={() => setForm(<About />)}>About</Link>
    </nav>
    </div>
  )
}
