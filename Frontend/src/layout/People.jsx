import React, { useState, useEffect } from 'react';
import axios from '../api/axios';

const BASE_URL = "http://localhost:5500";

export default function People({ showPanel, setShowPanel, extractedFaces = [], currentUser }) {
  const [faces, setFaces] = useState([]);
  const [peopleNames, setPeopleNames] = useState({});
  const [isEditing, setIsEditing] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  // Update faces when extractedFaces prop changes
  useEffect(() => {
    if (extractedFaces && extractedFaces.length > 0) {
      setFaces(extractedFaces);
      const names = {};
      extractedFaces.forEach((face, i) => {
        names[i] = face.face_tag || `Person ${i + 1}`;
      });
      setPeopleNames(names);
    }
  }, [extractedFaces]);

  const handleNameChange = (index, name) => {
    setPeopleNames((prev) => ({
      ...prev,
      [index]: name,
    }));
  };

  const handleCircleClick = (index) => {
    setIsEditing((prev) => ({
      ...prev,
      [index]: true,
    }));
  };

  const handleAdd = async (index) => {
    setIsEditing((prev) => ({
      ...prev,
      [index]: false,
    }));

    const oldTag = faces[index].face_tag;
    const newTag = peopleNames[index];
    if (!newTag || newTag === oldTag) return;

    setIsLoading(true);
    try {
      const res = await axios.post('/model/change_face_tag', {
        user_id: currentUser?._id,
        face_tag: oldTag,
        new_face_tag: newTag,
      });

      if (res.status === 200) {
        const updatedFaces = [...faces];
        updatedFaces[index].face_tag = newTag;
        setFaces(updatedFaces);
        console.log("Face tag updated successfully");
      } else {
        console.log("Failed to rename FaceTag");
      }
    } catch (error) {
      console.log("Error updating face tag:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (index) => {
    const faceToDelete = faces[index];
    if (!faceToDelete) return;

    setIsLoading(true);
    try {
      const res = await axios.post('/model/delete_face_tag', {
        user_id: currentUser?._id,
        face_tag: faceToDelete.face_tag,
      });

      if (res.status === 200) {
        const newFaces = faces.filter((_, i) => i !== index);
        setFaces(newFaces);
        const newNames = { ...peopleNames };
        delete newNames[index];
        setPeopleNames(newNames);
        console.log("Face deleted successfully");
      } else {
        console.log("Failed to delete face");
      }
    } catch (error) {
      console.log("Error deleting face:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderUserCircles = () => {
    if (faces.length === 0) {
      return (
        <div className="text-center text-gray-400 py-8">
          <p>No faces detected yet.</p>
          <p className="text-sm mt-2">Initialize your memory to extract faces from your photos.</p>
        </div>
      );
    }

    return faces.map((face, i) => (
      <div key={face.id || i} className="relative flex flex-col items-center justify-center mb-6 mr-4">
        {/* Delete button */}
        <button
          onClick={() => handleDelete(i)}
          className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs z-10 hover:bg-red-800 transition-colors"
          title="Delete"
          disabled={isLoading}
        >
          ×
        </button>

        {/* Circle with image */}
        <div
          onClick={() => handleCircleClick(i)}
          className="w-20 h-20 rounded-full bg-gray-600 flex items-center justify-center cursor-pointer relative border-2 border-gray-500 hover:border-purple-400 transition-colors overflow-hidden"
          style={{
            backgroundImage: face.imageUrl ? `url(${face.imageUrl})` : 'none',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {!face.imageUrl && (
            <span className="text-white text-2xl">👤</span>
          )}
        </div>

        {/* Name input/display */}
        <div className="mt-2 w-24">
          {isEditing[i] ? (
            <input
              type="text"
              value={peopleNames[i] || ''}
              onChange={(e) => handleNameChange(i, e.target.value)}
              onBlur={() => handleAdd(i)}
              onKeyPress={(e) => e.key === 'Enter' && handleAdd(i)}
              autoFocus
              className="bg-gray-700 text-white text-center w-full text-xs p-1 rounded border border-gray-600 focus:border-purple-400 focus:outline-none"
              placeholder="Name"
              disabled={isLoading}
            />
          ) : (
            <span
              className="text-white text-xs text-center block cursor-pointer hover:text-purple-300 transition-colors break-words"
              onClick={() => handleCircleClick(i)}
            >
              {peopleNames[i] || 'Unknown'}
            </span>
          )}
        </div>
      </div>
    ));
  };

  return (
    <div
      className={`fixed top-0 right-0 h-full w-80 bg-gray-800 text-white shadow-lg transform transition-transform duration-300 z-50 ${showPanel ? 'translate-x-0' : 'translate-x-full'
        }`}
    >
      <div className="p-4 relative h-full overflow-y-auto">
        <button
          onClick={() => setShowPanel(false)}
          className="absolute top-4 right-4 text-red-500 hover:text-red-700 text-xl font-bold focus:outline-none z-10"
          aria-label="Close"
        >
          &times;
        </button>

        <h2 className="text-xl font-bold mb-4 font-serif">Discover People</h2>

        {extractedFaces.length > 0 ? (
          <p className="text-sm text-gray-300 mb-4">
            Found {extractedFaces.length} face(s) in your photos. Click on any face to give it a name.
          </p>
        ) : (
          <p className="text-sm text-gray-300 mb-4">
            You can manage people here or associate them with your memories. Initialize your memory to extract faces from photos.
          </p>
        )}

        {/* Status indicator */}
        {isLoading && (
          <div className="mb-4 p-2 bg-blue-600 text-white rounded text-sm">
            Processing...
          </div>
        )}

        <p className="text-lg font-semibold text-purple-400 mt-4 mb-4 text-center">
          {faces.length > 0 ? 'Click to name each person' : 'No faces detected'}
        </p>

        <div className="flex flex-wrap justify-center">
          {renderUserCircles()}
        </div>

        {/* Instructions */}
        {faces.length > 0 && (
          <div className="mt-6 p-3 bg-gray-700 rounded text-xs text-gray-300">
            <p className="font-semibold mb-2">Instructions:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Click on a face to edit the name</li>
              <li>Press Enter or click outside to save</li>
              <li>Click the × button to delete a face</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}