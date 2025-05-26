import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:5000', // base URL
  withCredentials: true, // To send cookies like accessToken
});

export default instance;
