import { useState, useMemo } from "react"
import PasswordValidator from "./PasswordValidator";
import MobileValidator from "./MobileValidator";
import EmailValidator from "./EmailValidator";
import { useNavigate } from 'react-router-dom';
import { Link } from "react-router-dom";

export default function Register() {

    const [userImage, setUserImage] = useState(null);
    const navigate = useNavigate();
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [mobile, setMobile] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [passwordConfirmation, setPasswordConfirmation] = useState('');

    console.log('Register Component Rendered');

    //First Name
    const handle_firstname_change = (e) => {

        const text = e.target.value;
        if (text.length >= 21) {
            return
        }
        setFirstName(text);
    }
    const firstnameValidator = useMemo(() => {
        console.log('firstnameValidator component rendered');
        const len = firstName.length;
        if (len === 0) {
            return <span className="text-xs text-sky-400">Must be between 3 and 21 characters</span>
        }
        if (len < 3) {
            return <span className="text-xs text-red-400">Can't be less than 3 characters</span>
        }
        if (len <= 20) {
            return <span className="text-xs text-green-400">First name accepted</span>
        }
    }, [firstName])

    // Last Name
    const handle_lastname_change = (e) => {

        const text = e.target.value;
        if (text.length >= 21) {
            return
        }
        setLastName(text);
    }
    const LastnameValidator = useMemo(() => {
        console.log('LastnameValidator component rendered');

        const len = lastName.length;

        if (len === 0) {
            return <span className="text-sky-500">must be from 3 to 20 characters</span>
        }

        if (len < 3) {
            return <span className="text-red-500">can't be less than 3 characters</span>
        }

        if (len < 21) {
            return <span className="text-green-500">Last name accepted</span>
        }
    }, [lastName])

    //mobile
    const handle_mobile_change = (e) => {
        const text = e.target.value;

        if (text.length > 11) {
            return
        }
        setMobile(text);
    }

    //email
    const handle_email_change = (e) => {
        const text = e.target.value;
        setEmail(text);
    }

    //password
    const handle_pass_change = e => setPassword(e.target.value)

    //passwordConfiramtion
    const handle_conf_pass_change = e => setPasswordConfirmation(e.target.value);

    const handleSubmit = (e) => {
        e.preventDefault();

        // You can add form validation here if needed

        // Example: only navigate if all fields are filled
        if (firstName && lastName && mobile && email && password && passwordConfirmation) {
            navigate('/init');
        } else {
            alert('Please fill in all required fields');
        }
    }
    //image upload
    const handleImageUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            const imageURL = URL.createObjectURL(file);
            setUserImage(imageURL);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen p-6">
            <div className="w-full max-w-md p-8 space-y-6 rounded-lg shadow-lg">
                <h1 className="text-xl font-bold text-white text-center md:text-2xl dark:text-white">
                    Create an account
                </h1>
                <form className="space-y-4 md:space-y-6" onSubmit={handleSubmit}>

                    {/* First Name */}
                    <div>
                        <label htmlFor="firstname" className="block mb-2 text-sm font-medium text-white">First Name</label>
                        <input value={firstName} onChange={handle_firstname_change} type="text" id="firstname" className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" placeholder="First Name" />
                        <p className="flex justify-between text-xs">
                            {firstnameValidator}
                            <span className="text-sky-500">{firstName.length}/20</span>
                        </p>
                    </div>

                    {/* Last Name */}
                    <div>
                        <label htmlFor="lastname" className="block mb-2 text-sm font-medium text-white">Last Name</label>
                        <input value={lastName} onChange={handle_lastname_change} type="text" id="lastname" className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" placeholder="Last Name" />
                        <p className="flex justify-between text-xs">

                            {LastnameValidator}

                            <span className="text-sky-500 text-xs">{lastName.length}/20</span>
                        </p>
                    </div>

                    {/* User Upload picture */}
                    <div className="space-y-4">
                        <div className="flex items-center space-x-4">
                            {/* File Input */}
                            <div>
                                <label htmlFor="userImage" className="block text-sm font-medium text-white">Profile Picture</label>
                                <input
                                    id="userImage"
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    className="w-full p-2 bg-gray-700 border border-gray-600 text-white rounded"
                                />
                            </div>

                            {/* Image Preview */}
                            {userImage && (
                                <div className="mt-2">
                                    <img
                                        src={userImage}
                                        alt="Profile preview"
                                        className="w-24 h-24 rounded-full object-cover"
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                    {/* Mobile number */}
                    <div>
                        <label htmlFor="mobile" className="block mb-2 text-sm font-medium text-white">Mobile</label>
                        <input value={mobile} onChange={handle_mobile_change} type="text" id="mobile" className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" placeholder="Mobile" />
                        <MobileValidator mobile={mobile} />
                    </div>

                    {/* Email */}
                    <div>
                        <label htmlFor="email" className="block mb-2 text-sm font-medium text-white">Email</label>
                        <input value={email} onChange={handle_email_change} type="email" id="email" className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" placeholder="email" />
                        <EmailValidator email={email} />
                    </div>

                    {/* Password */}
                    <div>
                        <label htmlFor="password" className="block mb-2 text-sm font-medium text-white">Password</label>
                        <input value={password} onChange={handle_pass_change} type="password" id="password" placeholder="••••••••" className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" />
                    </div>

                    {/* password Confirmation */}
                    <div>
                        <label htmlFor="password_confirmation" className="block mb-2 text-sm font-medium text-white">Confirm Password</label>
                        <input value={passwordConfirmation} onChange={handle_conf_pass_change} type="password" id="confirm-password" placeholder="••••••••" className="bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" />
                    </div>

                    <PasswordValidator password={password} passwordConfirmation={passwordConfirmation} />

                    <div className="text-center mt-4">
                        <span className="text-sm text-gray-300">
                            Already have an account?{' '}
                            <Link to="/login" className="text-indigo-400 hover:underline font-medium">
                                Login
                            </Link>
                        </span>
                    </div>

                    {/* register submit button */}
                    <button
                        type="submit"
                        className="w-full bg-indigo-600 text-white font-semibold rounded-xl text-lg py-2.5 px-5 hover:bg-indigo-700 transition duration-300 shadow-md">Create an Account</button>

                </form>
            </div>
        </div>
    )
}