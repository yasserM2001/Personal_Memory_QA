import React, { useState, useEffect } from 'react';
import axios from '../api/axios';

export default function People({ showPanel, setShowPanel, extractedFaces = [], currentUser }) {
  const [faces, setFaces] = useState([]);
  const [peopleNames, setPeopleNames] = useState({});
  const [isEditing, setIsEditing] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Update faces when extractedFaces prop changes
  useEffect(() => {
    if (extractedFaces && extractedFaces.length > 0) {
      console.log('🔄 Initial faces received:', extractedFaces.length);
      setFaces(extractedFaces);
      const names = {};
      extractedFaces.forEach((face, i) => {
        names[i] = face.face_tag || `Person ${i + 1}`;
      });
      setPeopleNames(names);
    }
  }, [extractedFaces]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Helper function to update faces from backend response
  const updateFacesFromResponse = (extractedFaces) => {
    console.log('🔄 Updating faces from backend response:', extractedFaces?.length || 0);
    
    // Log the first few faces to see their structure
    if (extractedFaces && extractedFaces.length > 0) {
      console.log('📋 Sample faces received:', extractedFaces.slice(0, 3));
      
      // Check for duplicates by face_tag
      const faceTagCounts = {};
      extractedFaces.forEach(face => {
        faceTagCounts[face.face_tag] = (faceTagCounts[face.face_tag] || 0) + 1;
      });
      
      const duplicates = Object.entries(faceTagCounts).filter(([tag, count]) => count > 1);
      if (duplicates.length > 0) {
        console.warn('⚠️ Duplicate face tags detected:', duplicates);
      }
      
      // Convert extracted_faces to the format expected by the frontend
      const convertedFaces = extractedFaces.map((face, index) => ({
        id: index + 1,
        face_tag: face.face_tag,
        filename: face.filename,
        base64_image: face.base64_image,
        imageUrl: face.imageUrl || `data:image/jpeg;base64,${face.base64_image?.replace(/^data:image\/\w+;base64,/, "") || ""}`,
        total_faces_in_group: face.total_faces_in_group || 1
      }));
      
      console.log('✅ Converted faces for display:', convertedFaces.length);
      setFaces(convertedFaces);
      
      // Update names
      const names = {};
      convertedFaces.forEach((face, i) => {
        names[i] = face.face_tag || `Person ${i + 1}`;
      });
      setPeopleNames(names);
    } else {
      console.log('🧹 No faces returned, clearing display');
      setFaces([]);
      setPeopleNames({});
    }
    
    // Clear editing states
    setIsEditing({});
  };

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
    if (!newTag || newTag === oldTag) {
      console.log('❌ No change needed, names are the same');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log(`🔄 Changing face tag from "${oldTag}" to "${newTag}"`);
      
      const res = await axios.post('/model/change_face_tag', {
        user_id: currentUser?._id,
        face_tag: oldTag,
        new_face_tag: newTag,
      });

      if (res.status === 200) {
        console.log('✅ Face tag updated successfully');
        console.log('📊 Backend response:', res.data);
        setError('Face tag updated successfully');
        
        // Update faces from the backend response
        if (res.data.extracted_faces) {
          updateFacesFromResponse(res.data.extracted_faces);
        }
      } else {
        console.log('❌ Failed to rename FaceTag');
        setError('Failed to rename FaceTag');
      }
    } catch (error) {
      console.error('❌ Error updating face tag:', error);
      setError(error.response?.data?.error || 'Error updating face tag');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (index) => {
    const faceToDelete = faces[index];
    if (!faceToDelete) return;

    const tagToDelete = faceToDelete.face_tag;
    
    // Show confirmation dialog
    if (!window.confirm(`Are you sure you want to delete "${tagToDelete}"?`)) {
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log(`🗑️ Deleting face tag "${tagToDelete}"`);
      
      const res = await axios.post('/model/delete_face_tag', {
        user_id: currentUser?._id,
        face_tag: tagToDelete,
      });

      if (res.status === 200) {
        console.log('✅ Face deleted successfully');
        console.log('📊 Backend response:', res.data);
        setError('Face deleted successfully');
        
        // Update faces from the backend response
        if (res.data.extracted_faces !== undefined) {
          updateFacesFromResponse(res.data.extracted_faces);
        }
      } else {
        console.log('❌ Failed to delete face');
        setError('Failed to delete face');
      }
    } catch (error) {
      console.error('❌ Error deleting face:', error);
      setError(error.response?.data?.error || 'Error deleting face');
    } finally {
      setIsLoading(false);
    }
  };

  // Debug function to analyze current faces
  const analyzeFaces = () => {
    console.log('🔍 Current faces analysis:');
    console.log('Total faces:', faces.length);
    
    const tagCounts = {};
    faces.forEach(face => {
      tagCounts[face.face_tag] = (tagCounts[face.face_tag] || 0) + 1;
    });
    
    console.log('Face tag distribution:', tagCounts);
    
    const duplicateTags = Object.entries(tagCounts).filter(([tag, count]) => count > 1);
    if (duplicateTags.length > 0) {
      console.warn('⚠️ Faces with duplicate tags:', duplicateTags);
    }
    
    console.log('Sample faces:', faces.slice(0, 5));
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
        >
          {face.imageUrl ? (
            <img
              src={face.imageUrl}
              alt={`Face ${i + 1}`}
              className="w-full h-full object-cover rounded-full"
              onError={(e) => {
                console.error(`❌ Failed to load image: ${face.imageUrl}`);
                e.target.style.display = 'none';
                e.target.parentElement.innerHTML += '<span class="text-white text-2xl">👤</span>';
              }}
            />
          ) : (
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

        {/* Face count badge - show if this represents multiple faces */}
        {face.total_faces_in_group > 1 && (
          <div className="mt-1 bg-purple-600 text-white text-xs px-2 py-0.5 rounded-full">
            {face.total_faces_in_group} faces
          </div>
        )}
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

        {/* Debug button - remove in production */}
        <button
          onClick={analyzeFaces}
          className="mb-2 bg-purple-600 hover:bg-purple-700 text-white px-2 py-1 rounded text-xs"
        >
          🔍 Debug Faces
        </button>

        {faces.length > 0 ? (
          <p className="text-sm text-gray-300 mb-4">
            Found {faces.length} unique person(s) in your photos. Click on any face to give it a name.
          </p>
        ) : (
          <p className="text-sm text-gray-300 mb-4">
            You can manage people here or associate them with your memories. Initialize your memory to extract faces from photos.
          </p>
        )}

        {/* Status indicator */}
        {isLoading && (
          <div className="mb-4 p-2 bg-blue-600 text-white rounded text-sm flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </div>
        )}

        {error && (
          <div className={`mb-4 p-2 rounded text-sm text-center font-semibold ${error.toLowerCase().includes('success') ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
            }`}>
            {error}
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
              <li>Changes are automatically synced</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}