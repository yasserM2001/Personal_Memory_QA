import { useState, useMemo } from "react"
import PasswordValidator from "./PasswordValidator";
import MobileValidator from "./MobileValidator";
import EmailValidator from "./EmailValidator";
import Initialize from "../../pages/Initialize";

export default function Register() {

    const [init , setInitialize ] = useState(false);

    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [mobile, setMobile] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [passwordConfirmation, setPasswordConfirmation] = useState('');

    console.log('Register Component Rendered');

    //First Name
    const handle_firstname_change = (e) =>{

        const text = e.target.value;
        if(text.length >= 21){
            return
        } 
        setFirstName(text);
    }
    const firstnameValidator = useMemo(()=>{
        console.log('firstnameValidator component rendered');
        const len =firstName.length;
        if(len == 0){
            return <span className="text-xs text-sky-400">Must be between 3 and 21 characters</span>
        }
        if(len < 3){
            return <span className="text-xs text-red-400">Can't be less than 3 characters</span>
        }        
        if(len <=20){
            return <span className="text-xs text-green-400">First name accepted</span>
        }
    },[firstName])

    // Last Name
    const handle_lastname_change = (e) =>{

        const text = e.target.value;
        if(text.length >= 21){
            return
        }
        setLastName(text);
    }
    const LastnameValidator = useMemo(()=>{
        console.log('LastnameValidator component rendered');

        const len = lastName.length;

        if(len == 0){
            return <span className="text-sky-500">must be from 3 to 20 characters</span>
        }     

        if(len < 3){
            return <span className="text-red-500">can't be less than 3 characters</span>
        }        
        
        if(len < 21){
            return <span className="text-green-500">Last name accepted</span>
        }
    },[lastName])

    //mobile
    const handle_mobile_change = (e) =>{
        const text = e.target.value;

        if(text.length > 11){
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
    
    return (
        <div className="flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-md p-8 space-y-6 rounded-lg shadow-lg">
              <h1 className="text-xl font-bold text-white text-center md:text-2xl dark:text-white">
                Create an account
            </h1>
            <form className="space-y-4 md:space-y-6" action="init">

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
                    <EmailValidator email={email}/>
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

                <button 
                    onClick={()=>setInitialize(<Initialize/>)}
                    type="submit" 
                    id='init'
                    className="w-full bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-4 focus:outline-none focus:ring-indigo-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center transition duration-300">
                    Create an Account
                </button>   
          
         </form>
        </div>
    </div>
        )
}