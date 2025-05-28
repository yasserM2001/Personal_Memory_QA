import React, { useState, useEffect } from 'react';
import { Button, FileInput, Label, TextInput } from "flowbite-react";
import image from '../assets/imgs/image.png';
import People from '../layout/People';
import DropDownMenu from '../layout/DropDownMenu';
import { useNavigate } from "react-router-dom";
import axios from '../api/axios';

const DETECT_FACES = true;

export default function Initialize() {
  const [currentUser, setCurrentUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
      navigate("/login");
    } else {
      setCurrentUser(user);
    }
  }, [navigate]);

  const [showPanel, setShowPanel] = useState(false);
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('');
  const [files, setFiles] = useState([]);
  const [answer, setAnswer] = useState('');
  const [evidence, setEvidence] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // New state for extracted faces
  const [extractedFaces, setExtractedFaces] = useState([]);
  const [initializationData, setInitializationData] = useState(null);

  console.log("Extracted Faces:", extractedFaces);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setError("Please upload your data first");
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('user_id', currentUser._id);
      Array.from(files).forEach(f => {
        formData.append('files', f);
      });

      const res = await axios.post('/model/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        withCredentials: true
      });

      setEvidence(res.data.evidence);
    } catch (err) {
      setError(err.response?.data?.error || "Upload failed");
      console.error("Upload error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInitialize = async () => {
    setIsLoading(true);
    setError('');
    setExtractedFaces([]); // Clear previous faces

    try {
      const res = await axios.post('/model/initialize', {
        user_id: currentUser._id,
        detect_faces: DETECT_FACES
      });

      const data = res.data;

      // Set the response message
      // setAnswer(data.message || "Initialization successful");

      // Store the full initialization data
      setInitializationData(data);

      // Handle extracted faces
      if (data.saved_image_paths && data.saved_image_paths.length > 0) {
        console.log('Saved image paths:', data.saved_image_paths); // Debug log

        // Convert saved image paths to face objects
        const faces = data.saved_image_paths.map((imagePath, index) => {
          // Remove any leading slashes or backslashes and normalize path separators
          const normalizedPath = imagePath.replace(/^[\/\\]+/, '').replace(/\\/g, '/');

          // Since savedPaths already includes 'saved_faces/userId/filename.jpg'
          // we just need to prepend the base URL
          const imageUrl = `http://localhost:5500/${normalizedPath}`;

          console.log(`Face ${index + 1} URL:`, imageUrl); // Debug log

          return {
            id: index + 1,
            face_tag: `face_${index + 1}`,
            imageUrl: imageUrl,
            imagePath: imagePath
          };
        });

        setExtractedFaces(faces);

        // Automatically open the People panel when faces are found
        setShowPanel(true);
      } else if (data.extracted_faces && data.extracted_faces.length > 0) {
        // Fallback to extracted_faces if saved_image_paths is not available
        const faces = data.extracted_faces.map((face, index) => ({
          id: index + 1,
          face_tag: `face_${index + 1}`,
          imageUrl: face, // Assuming this contains the image URL or path
          imagePath: face
        }));
        setExtractedFaces(faces);
        setShowPanel(true);
      }

    } catch (err) {
      setError(err.response?.data?.error || "Failed to initialize");
      console.error("Initialize error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      setError("Please enter a question");
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const res = await axios.post('/model/query', {
        user_id: currentUser._id,
        query,
        method: method || '',
        detect_faces: DETECT_FACES,
        topk: 5
      });

      setAnswer(res.data.answer);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to get the answer, try again...");
      console.error("Query error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl p-4 bg-opacity-25 bg-slate-900 rounded shadow-md">
        {/* Error Display */}
        {error && (
          <div className="mb-4 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Success Message for Initialization */}
        {!error && initializationData && (
          <div className="mb-4 p-2 bg-green-100 border border-green-400 text-green-700 rounded">
            <div className="flex items-center justify-between">
              <span>{answer}</span>
              {extractedFaces.length > 0 && (
                <span className="text-sm font-medium">
                  {extractedFaces.length} faces found
                </span>
              )}
            </div>
          </div>
        )}

        {/* File Upload */}
        <div className="mb-4 border-neutral-700 p-4">
          <div className='flex items-center gap-2'>
            <div className='h-full w-full'>
              <Label htmlFor="file-upload-helper-text" value="Upload file" className="text-gray-300" />
              <FileInput
                multiple
                id="file-upload-helper-text"
                helperText="SVG, PNG, JPG or GIF."
                className="w-full"
                onChange={handleFileChange}
                disabled={isLoading}
              />
            </div>
            <Button
              className="bg-blue-800 text-white w-25 py-2 h-full"
              onClick={handleUpload}
              disabled={isLoading}
            >
              {isLoading ? 'Uploading...' : 'Upload'}
            </Button>
          </div>
          <Button
            className="bg-blue-600 text-white py-2 mx-auto block my-auto"
            onClick={handleInitialize}
            disabled={isLoading}
          >
            {isLoading ? 'Initializing...' : 'Initialize'}
          </Button>
        </div>

        {/* People Button */}
        <div className="mt-4 text-center">
          <button
            onClick={() => setShowPanel(true)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 rounded-full shadow-lg hover:scale-105 transition-transform duration-300"
            disabled={isLoading}
          >
            ✨ People
            {extractedFaces.length > 0 && (
              <span className="bg-yellow-300 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded-full">
                {extractedFaces.length}
              </span>
            )}
            {extractedFaces.length === 0 && (
              <span className="bg-yellow-300 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded-full">
                New
              </span>
            )}
          </button>
        </div>

        {/* Question Input */}
        <div className="text-center p-4 m-4">
          <DropDownMenu selectedMethod={method} setSelectedMethod={setMethod} disabled={isLoading} />
          <Label htmlFor="base" value="Enter your Question" className="font-sans text-gray-300" />
          <div className='flex items-center gap-2'>
            <TextInput
              onChange={(e) => setQuery(e.target.value)}
              id="base"
              type="text"
              sizing="lg"
              className="bg-gray-200 border border-gray-300 rounded-md text-black text-lg w-full"
              disabled={isLoading}
            />
            <Button
              onClick={handleQuery}
              className="bg-green-400 text-white px-4 py-2 whitespace-nowrap"
              disabled={isLoading}
            >
              {isLoading ? 'Asking...' : 'Ask'}
            </Button>
          </div>
        </div>

        {/* Answer Output */}
        <div className="mt-6">
          <textarea
            readOnly
            value={answer}
            className="w-full h-40 p-3 border rounded bg-gray-100 focus:outline-none"
            placeholder={isLoading ? "Processing..." : "Answer will appear here..."}
          />
        </div>

        {/* Display Image */}
        <div className="mt-4">
          {evidence ? (
            <img src={evidence} alt="Uploaded evidence" className="rounded" />
          ) : (
            <img src={image} alt="Placeholder" />
          )}
        </div>

        {/* People Slide-In Panel - Pass extracted faces */}
        <People
          showPanel={showPanel}
          setShowPanel={setShowPanel}
          extractedFaces={extractedFaces}
          currentUser={currentUser}
        />
      </div>
    </div>
  );
}