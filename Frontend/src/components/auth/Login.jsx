import { useState, useMemo } from "react"
import EmailValidator from "./EmailValidator"
import Initialize from "../../pages/Initialize";

export default function Login() {
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');


  const [init , setInitialize ] = useState(false);
    
  //email
  const handle_email_change = (e) => {
    const text = e.target.value;
    setEmail(text);
  }

  //password
  const handle_pass_change = e => setPassword(e.target.value)

  return (
    <div className="flex items-center justify-center min-h-screen p-6">
      <div className="w-full max-w-md p-8 space-y-6 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold leading-tight tracking-tight text-white text-center">
          Sign in to your account
        </h1>
  
        <form className="space-y-4" action="init">
          <div>
            <label htmlFor="email" className="block mb-2 text-sm font-medium text-white">Email</label>
            <input 
              value={email} 
              onChange={handle_email_change} 
              type="email" 
              id="email" 
              className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" 
              placeholder="email" 
            />
            <EmailValidator email={email}/>
          </div>
  
          <div>
            <label htmlFor="password" className="block mb-2 text-sm font-medium text-white">Password</label>
            <input 
              value={password} 
              onChange={handle_pass_change} 
              type="password" 
              id="password" 
              placeholder="••••••••" 
              className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" 
            />
          </div>
  
          <button 
            onClick={()=>setInitialize(<Initialize/>)}
            type="submit" 
            id='init'
            className="w-full bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-4 focus:outline-none focus:ring-indigo-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center transition duration-300">
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
  
}