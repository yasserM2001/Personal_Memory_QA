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
  const [evidencePhotos, setEvidencePhotos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedPhoto, setSelectedPhoto] = useState(null);


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

      // Store the full initialization data
      setInitializationData(data);

      // Handle extracted faces
      if (data.saved_image_paths && data.saved_image_paths.length > 0) {
        console.log('Saved image paths:', data.saved_image_paths);

        // Convert saved image paths to face objects
        const faces = data.saved_image_paths.map((imagePath, index) => {
          const normalizedPath = imagePath.replace(/^[/\\]+/, '').replace(/\\/g, '/');
          const imageUrl = `http://localhost:5500/${normalizedPath}`;

          return {
            id: index + 1,
            face_tag: data.extracted_faces[index]?.face_tag || `face_${index + 1}`,
            imageUrl: imageUrl,
            imagePath: imagePath
          };
        });

        setExtractedFaces(faces);
        setShowPanel(true);
      } else if (data.extracted_faces && data.extracted_faces.length > 0) {
        const faces = data.extracted_faces.map((face, index) => ({
          id: index + 1,
          face_tag: `face_${index + 1}`,
          imageUrl: face,
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

    if (!method || method === '') {
      setError("Please select a model method");
      return;
    }

    setIsLoading(true);
    setError('');
    setEvidencePhotos([]); // Clear previous evidence

    try {
      const res = await axios.post('/model/query', {
        user_id: currentUser._id,
        query,
        method: method,
        detect_faces: DETECT_FACES,
        topk: 5
      });

      console.log('🔍 Query response:', res.data);

      // Set the answer
      setAnswer(res.data.response?.answer || res.data.answer || "No answer received");

      // Handle evidence photos
      if (res.data.evidence && res.data.evidence.length > 0) {
        console.log('📷 Evidence photos found:', res.data.evidence.length);

        // Convert file paths to URLs
        const photoUrls = res.data.evidence.map((filePath, index) => {
          // Extract filename from full path
          const filename = filePath.split(/[/\\]/).pop();
          // Create URL for serving the image
          const imageUrl = `http://localhost:5500/photos/${currentUser._id}/evidence/${filename}`;

          console.log(`Evidence ${index + 1}:`, imageUrl);

          return {
            id: index + 1,
            filename: filename,
            imageUrl: imageUrl,
            filePath: filePath
          };
        });

        setEvidencePhotos(photoUrls);
        // Set the first photo as main evidence for backward compatibility
        setEvidence(photoUrls[0]?.imageUrl);
      } else if (res.data.memory_photos && res.data.memory_photos.length > 0) {
        console.log('📷 Memory photos found:', res.data.memory_photos.length);

        // Handle memory photos with base64 data
        const photos = res.data.memory_photos.map((photo, index) => ({
          id: index + 1,
          filename: photo.filename,
          imageUrl: photo.base64_image,
          memory_id: photo.memory_id
        }));

        setEvidencePhotos(photos);
        setEvidence(photos[0]?.imageUrl);
      } else {
        console.log('❌ No evidence or memory photos found');
        setEvidence(null);
        setEvidencePhotos([]);
      }

    } catch (err) {
      setError(err.response?.data?.error || "Failed to get the answer, try again...");
      console.error("Query error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Component to display evidence photos gallery
  const EvidenceGallery = ({ photos }) => {
    if (!photos || photos.length === 0) {
      return null;
    }


    return (
      <div className="mt-4">
        <h3 className="text-lg font-semibold text-white mb-3">
          Evidence Photos ({photos.length})
        </h3>

        {/* Main display - show first photo large */}
        <div className="mb-4">
          <img
            src={photos[0].imageUrl}
            alt="Main evidence"
            className="w-full max-h-64 object-contain rounded border border-gray-600"
            onError={(e) => {
              console.error('Failed to load main evidence image:', photos[0].imageUrl);
              e.target.src = image; // Fallback to placeholder
            }}
          />
        </div>

        {/* Thumbnail gallery if multiple photos */}
        {photos.length > 1 && (
          <div className="grid grid-cols-4 gap-2">
            {photos.map((photo, index) => (
              <div
                key={photo.id}
                className="relative cursor-pointer"
                onClick={() => setEvidence(photo.imageUrl)}
              >
                <img
                  src={photo.imageUrl}
                  alt={`Evidence ${index + 1}`}
                  className="w-full h-16 object-cover rounded border border-gray-600 hover:border-blue-400 transition-colors"
                  onError={(e) => {
                    console.error(`Failed to load thumbnail ${index + 1}:`, photo.imageUrl);
                    e.target.src = image;
                  }}
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all rounded"></div>
              </div>
            ))}
          </div>
        )}

        {/* Modal for full-size viewing */}
        {selectedPhoto && (
          <div
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedPhoto(null)}
          >
            <div className="relative max-w-4xl max-h-full">
              <button
                onClick={() => setSelectedPhoto(null)}
                className="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-75"
              >
                ×
              </button>
              <img
                src={selectedPhoto.imageUrl}
                alt="Full size evidence"
                className="max-w-full max-h-full object-contain rounded"
              />
            </div>
          </div>
        )}
      </div>
    );
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
              <span>Initialization successful</span>
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
              value={query}
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

        {/* Evidence Photos Gallery */}
        {evidencePhotos.length > 0 ? (
          <EvidenceGallery photos={evidencePhotos} />
        ) : (
          /* Fallback single image display */
          <div className="mt-4">
            {evidence ? (
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Evidence</h3>
                <img src={evidence} alt="Evidence" className="w-full rounded border border-gray-600" />
              </div>
            ) : (
              <img src={image} alt="Placeholder" className="w-full rounded" />
            )}
          </div>
        )}

        {/* People Slide-In Panel */}
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