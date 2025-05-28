import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:5500', // base URL
  withCredentials: true, // To send cookies like accessToken
  credentials: 'include', // Include cookies in the request
});

// Response interceptor to handle token expiration
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default instance;
