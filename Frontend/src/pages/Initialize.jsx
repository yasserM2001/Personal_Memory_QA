import React from 'react'
import { Button, FileInput, Label, TextInput } from "flowbite-react";
import image from '../assets/imgs/image.png'

const Initialize = () => {
  return (
<div className="flex justify-center items-center min-h-screen">
  <div className="w-full max-w-sm p-4 bg-opacity-25 bg-slate-900 rounded shadow-md">
    <div className="mb-4">
      <Label htmlFor="file-upload-helper-text" value="Upload file" className="text-gray-300" />
      <FileInput
        id="file-upload-helper-text"
        helperText="SVG, PNG, JPG or GIF (MAX. 800x400px)."
        className="w-full"
      />
      <Button className="bg-blue-800 text-white w-full py-2">Upload</Button>
    </div>
    <div className="mb-6">
      <Label htmlFor="base" value="Please Enter your Question" className="font-sans text-gray-300" />
      <TextInput
        id="base"
        type="text"
        sizing="lg"
        className="bg-gray-200 border border-gray-300 text-black text-lg w-full mt-2"
      />
    </div>
    <Button className="bg-green-600 text-white w-full py-2">Ask</Button>
    <div className="mt-6">
      <textarea
        readOnly
        className="w-full h-40 p-3 border rounded bg-gray-100 focus:outline-none"
        placeholder="Answer will appear here..."
      />
    </div>
    <div className="mt-4">
      <img src={image} alt="The evidence" className="w-full h-auto rounded"/>
    </div>
  </div>
</div>

  );
}
export default Initialize;
