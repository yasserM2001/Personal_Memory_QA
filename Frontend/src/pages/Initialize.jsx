import React, { useState } from 'react';
import { Button, FileInput, Label, TextInput } from "flowbite-react";
import image from '../assets/imgs/image.png';
import People from '../layout/People';
import DropDownMenu from '../layout/DropDownMenu';

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";


const BASE_URL = "http://localhost:5000";
// const USER_ID = "test1";

export default function Initialize() {
  const [userNum, setUserNum] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
      navigate("/login");
    } else {
      setUserNum(String(user.user_num)); // Set state from localStorage
    }
  }, [navigate]);

  const [showPanel, setShowPanel] = useState(false);

  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('');
  const [files, setFiles] = useState([]);
  const [answer, setAnswer] = useState('');
  const [evidence, setEvidence] = useState(null);


  const handleFileChange = (e) => {
    setFiles(e.target.files);
  }
  const handleUpload = async () => {
    if (!files)
      return ("Please Upload your data first")

    const formData = new FormData();
    formData.append('user_id', userNum)
    Array.from(files).forEach(f => {
      formData.append('files', f);
    });

    const res = await fetch(`${BASE_URL}/model/upload`, {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const result = await res.json();
      setEvidence(result.evidence);
    } else {
      alert("Upload failed")
    }
  }

  const handleInitialize = async () => {
    const res = await fetch(`${BASE_URL}/model/initialize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userNum,
        detect_faces: false
      }),
    });
    if (res.ok) {
      const data = await res.json();
      setAnswer(data.answer || "Initialization successful");
    } else {
      setAnswer("Failed to answer , Error occured")
    }
  };

  const handleQuery = async () => {
    const res = await fetch(`${BASE_URL}/model/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userNum,
        query,
        method: method || '',
        detect_faces: false,
        topk: 5
      }),
    });
    if (res.ok) {
      const data = await res.json();
      setAnswer(data.answer);
    } else {
      setAnswer("Failed to get the answer , Try again ...")
    }
  };
  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="w-full max-w-sm p-4 bg-opacity-25 bg-slate-900 rounded shadow-md">

        {/* File Upload */}
        <div className="mb-4 border-neutral-700 p-4">
          <Label htmlFor="file-upload-helper-text" value="Upload file" className="text-gray-300" />
          <FileInput multiple id="file-upload-helper-text" helperText="SVG, PNG, JPG or GIF." className="w-full" onChange={handleFileChange} />
          <Button className="bg-blue-800 text-white w-full py-2" onClick={handleUpload}>Upload</Button>
          <Button className="bg-blue-800 text-white w-full py-2 my-3" onClick={handleInitialize}>Initialize</Button>
        </div>

        {/* People Button */}
        <div className="mt-4 text-center">
          <button
            onClick={() => setShowPanel(true)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 rounded-full shadow-lg hover:scale-105 transition-transform duration-300"
          >
            ✨ People <span className="bg-yellow-300 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded-full">New</span>
          </button>
        </div>

        {/* Question Input */}
        <div className="text-center p-4 m-4">
          <Label htmlFor="base" value="Enter your Question" className="font-sans text-gray-300" />
          <TextInput onChange={(e) => setQuery(e.target.value)} id="base" type="text" sizing="lg" className="bg-gray-200 border border-gray-300 rounded-md text-black text-lg w-full mt-2" />
          {/* Choose Model */}
          <DropDownMenu selectedMethod={method} setSelectedMethod={setMethod} />
          {/* Ask Button */}
          <Button onClick={handleQuery} className="bg-green-600 text-white w-full">Ask</Button>
        </div>


        {/* Answer Output */}
        <div className="mt-6">
          <textarea readOnly value={answer} className="w-full h-40 p-3 border rounded bg-gray-100 focus:outline-none" placeholder="Answer will appear here..." />
        </div>

        {/* Display Image */}
        <div className="mt-4">
          {evidence ? <img src={evidence} alt="Uploaded evidence" className="rounded" /> : <img src={image} alt="Placeholder" />}
        </div>

        {/* People Slide-In Panel (External Component) */}
        <People showPanel={showPanel} setShowPanel={setShowPanel} />
      </div>
    </div>
  );
}
