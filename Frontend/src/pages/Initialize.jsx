import React, { useState } from 'react';
import { Button, FileInput, Label, TextInput } from "flowbite-react";
import image from '../assets/imgs/image.png';
import People from '../layout/People';
import DropDownMenu from '../layout/DropDownMenu';

export default function Initialize() {
  const [showPanel, setShowPanel] = useState(false);

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="w-full max-w-sm p-4 bg-opacity-25 bg-slate-900 rounded shadow-md">

        {/* File Upload */}
        <div className="mb-4 border-neutral-700 p-4">
          <Label htmlFor="file-upload-helper-text" value="Upload file" className="text-gray-300" />
          <FileInput id="file-upload-helper-text" helperText="SVG, PNG, JPG or GIF." className="w-full" />
          <Button className="bg-blue-800 text-white w-full py-2">Upload</Button>
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
          <TextInput id="base" type="text" sizing="lg" className="bg-gray-200 border border-gray-300 rounded-md text-black text-lg w-full mt-2" />
          {/* Choose Model */}
          <DropDownMenu/>
        {/* Ask Button */}
        <Button className="bg-green-600 text-white w-full">Ask</Button>
        </div>


        {/* Answer Output */}
        <div className="mt-6">
          <textarea readOnly className="w-full h-40 p-3 border rounded bg-gray-100 focus:outline-none" placeholder="Answer will appear here..." />
        </div>

        {/* Display Image */}
        <div className="mt-4">
          <img src={image} alt="The evidence" className="w-full h-auto rounded" />
        </div>

      {/* People Slide-In Panel (External Component) */}
      <People showPanel={showPanel} setShowPanel={setShowPanel} />
    </div>
      </div>
  );
}
