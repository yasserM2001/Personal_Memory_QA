import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Home from './Home';
import Register from '../components/auth/Register';
import Initialize from './Initialize';
import Login from '../components/auth/Login';
import About from './About';
import ProtectedRoute from '../components/auth/ProtectedRoute';

export default function Pages() {
  return (
    <div>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/register' element={<Register />} />
          <Route path='/login' element={<Login />} />
          <Route 
            path='/init' 
            element={
              <ProtectedRoute>
                <Initialize />
              </ProtectedRoute>
            } 
          />
          <Route 
            path='/about' 
            element={
              <ProtectedRoute>
                <About />
              </ProtectedRoute>
            } 
          />
          {/* Redirect any unknown routes to home */}
          <Route path='*' element={<Navigate to="/" replace />} />
        </Routes>
    </div>
  );
}