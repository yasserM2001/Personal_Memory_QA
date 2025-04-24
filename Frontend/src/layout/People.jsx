import React, { useState, useEffect } from 'react';

export default function People({ showPanel, setShowPanel }) {
  // Example: Fetching faces from the backend (replace this with your API call)
  
  const [faces, setFaces] = useState([]);
  const [peopleNames, setPeopleNames] = useState({});
  const [isEditing, setIsEditing] = useState({}); // Track if a circle is being edited

  // Simulating an API call to fetch faces
  useEffect(() => {
    // Simulating a fetch call for the faces (replace with actual API call)
    const fetchedFaces = [
      { id: 1, imageUrl: 'https://example.com/face1.jpg' },
      { id: 2, imageUrl: 'https://example.com/face2.jpg' },
      { id: 3, imageUrl: 'https://example.com/face3.jpg' },
      //replace URLs with actual URLs from the backend
    ];
    setFaces(fetchedFaces);
  }, []);

  // Handle input change for names
  const handleNameChange = (index, name) => {
    setPeopleNames((prev) => ({
      ...prev,
      [index]: name,
    }));
  };

  // Handle click event to start editing
  const handleCircleClick = (index) => {
    setIsEditing((prev) => ({
      ...prev,
      [index]: true,
    }));
  };

  // Handle blur event (when the user clicks away from the input)
  const handleBlur = (index) => {
    setIsEditing((prev) => ({
      ...prev,
      [index]: false,
    }));
  };

  const renderUserCircles = () => {
    return faces.map((face, i) => (
      <div key={i} className="relative flex items-center justify-center mb-4 mr-4">
        {/* Circle with image or placeholder */}
        <div
          onClick={() => handleCircleClick(i)} // Handle circle click
          className="w-16 h-16 rounded-full bg-gray-600 flex items-center justify-center cursor-pointer relative"
          style={{
            backgroundImage: face.imageUrl ? `url(${face.imageUrl})` : 'none',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {/* If editing, show input field, otherwise show name or default photo */}
          {isEditing[i] ? (
            <input
              type="text"
              value={peopleNames[i] || ''}
              onChange={(e) => handleNameChange(i, e.target.value)}
              onBlur={() => handleBlur(i)} // Handle blur to stop editing
              autoFocus
              className="bg-transparent text-white text-center w-full"
              placeholder="Name"
            />
          ) : (
            <span className="text-white text-2xl">{peopleNames[i] || '?'}</span>
          )}
        </div>
      </div>
    ));
  };

  return (
    <div
      className={`fixed top-0 right-0 h-full w-64 bg-gray-800 text-white shadow-lg transform transition-transform duration-300 z-50 ${
        showPanel ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      <div className="p-2 relative">
        <button
          onClick={() => setShowPanel(false)}
          className="absolute top-2 right-2 text-red-500 hover:text-red-700 text-xl font-bold focus:outline-none"
          aria-label="Close"
        >
          &times;
        </button>
        <h2 className="text-xl font-bold mb-4 p-4 font-serif">Discover People</h2>
        <p className="text-sm text-gray-300 mb-4">You can manage people here or associate them with your memories. Enter a name for each person.</p>        
        <img src="people-remove.png" alt="people" className="w-full h-20 object-cover" />
        <p className="text-lg font-semibold text-purple-700 mt-2 mb-4 text-center">Enter a name for each person</p>
        <div className="flex flex-wrap">{renderUserCircles()}</div>
      </div>
    </div>
  );
}
