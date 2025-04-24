import { useState } from "react";
import { useNavigate } from "react-router-dom";
import EmailValidator from "./EmailValidator";
import { Link } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  // email
  const handle_email_change = (e) => {
    setEmail(e.target.value);
  };

  // password
  const handle_pass_change = (e) => {
    setPassword(e.target.value);
  };

  // on submit
  const handleSubmit = (e) => {
    e.preventDefault();

    // You can add form validation logic here

    // Redirect to /initialize
    navigate("/init");
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-6">
      <div className="w-full max-w-md p-8 space-y-6 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold leading-tight tracking-tight text-white text-center">
          Sign in to your account
        </h1>

        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block mb-2 text-sm font-medium text-white">Email</label>
            <input
              value={email}
              onChange={handle_email_change}
              type="email"
              id="email"
              className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"
              placeholder="email"
              required
            />
            <EmailValidator email={email} />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block mb-2 text-sm font-medium text-white">Password</label>
            <input
              value={password}
              onChange={handle_pass_change}
              type="password"
              id="password"
              placeholder="••••••••"
              className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"
              required
            />
          </div>
                    <div className="text-center mt-4">
                        <span className="text-sm text-gray-300">
                            New? Create an account{' '}
                            <Link to="/register" className="text-indigo-400 hover:underline font-medium">
                                register
                            </Link>
                        </span>
                    </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-4 focus:outline-none focus:ring-indigo-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center transition duration-300"
          >
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
}
