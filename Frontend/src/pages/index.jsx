import { Route, Routes } from 'react-router-dom'
// pages
import Home from './Home';
import Register from '../components/auth/Register';
import Initialize from './Initialize';
import Login from '../components/auth/Login';
import About from './About';

export default function Pages() {
  return (
    <div className="p-4">
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/register' element={<Register />} />
        <Route path='/init' element={<Initialize />} />
        <Route path='/login' element={<Login />} />
        <Route path='/about' element={<About />} />

        
      </Routes>
    </div>
  )
}
