import React from 'react'
import { useState } from 'react';
import Register from '../components/auth/Register';
export default function Home() {

    const [form, setForm] = useState("");

    return (
        <div className="text-white font-sans flex items-center justify-center min-h-screen flex-col">
            <div className="text-center px-6 py-12 max-w-lg w-full">
                <h1 className="text-4xl font-extrabold text-indigo-400 mb-6 fade-in">
                    Welcome to Your Personal Assistant Q&A!
                </h1>
                <p className="text-lg text-gray-300 mb-8 fade-in">
                    Ever wondered what stories your photos hold? Our intelligent assistant can help answer your life’s questions based on the photos and videos stored on your device.
                </p>
                <p className="text-base text-gray-400 mb-10 fade-in">
                    Simply upload your photos, ask questions, and discover insights about your memories like never before.
                </p>

                <div className=''>
                <button onClick={()=>setForm(<Register/>)} className="bg-indigo-600 text-white px-6 py-3 rounded-md text-lg font-semibold shadow-md transition duration-300 hover:bg-indigo-700 hover:shadow-lg fade-in">
                   <a href="/register">Get Started</a>
                </button>
                </div>

            </div>
            <div id='register'>
            {form}
            </div>

            <style jsx>{`
        @keyframes fadeIn {
            0% {
                opacity: 0;
                transform: translateY(20px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                    }
                    }
                    
                    .fade-in {
                        animation: fadeIn 1.5s ease-out;
                        }
                        `}</style>
        </div>
    );
};