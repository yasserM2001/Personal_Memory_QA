import React, { useState, useEffect } from 'react';

const BASE_URL = "http://localhost:5500";
const USER_ID = "test1";

export default function People({ showPanel, setShowPanel }) {
  const [faces, setFaces] = useState([]);
  const [peopleNames, setPeopleNames] = useState({});
  const [isEditing, setIsEditing] = useState({});

  useEffect(() => {
    const fetchedFaces = [
      { id: 1, face_tag: 'face1', imageUrl: 'https://example.com/face1.jpg' },
      { id: 2, face_tag: 'face2', imageUrl: 'https://example.com/face2.jpg' },
      { id: 3, face_tag: 'face3', imageUrl: 'https://example.com/face3.jpg' },
    ];
    setFaces(fetchedFaces);
    const names = {};
    fetchedFaces.forEach((f, i) => names[i] = f.face_tag);
    setPeopleNames(names);
  }, []);

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

    try {
      const res = await fetch(`${BASE_URL}/model/change_face_tag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          face_tag: oldTag,
          new_face_tag: newTag,
        }),
      });

      if (res.ok) {
        const updatedFaces = [...faces];
        updatedFaces[index].face_tag = newTag;
        setFaces(updatedFaces);
      } else {
        console.log("Failed to rename FaceTag");
      }
    } catch (error) {
      console.log("Error updating face tag:", error);
    }
  };

  const handleDelete = async (index) => {
    const faceToDelete = faces[index];
    if (!faceToDelete) return;

    try {
      const res = await fetch(`${BASE_URL}/model/delete_face_tag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          face_tag: faceToDelete.face_tag,
        }),
      });

      if (res.ok) {
        const newFaces = faces.filter((_, i) => i !== index);
        setFaces(newFaces);
        const newNames = { ...peopleNames };
        delete newNames[index];
        setPeopleNames(newNames);
      } else {
        console.log("Failed to delete face");
      }
    } catch (error) {
      console.log("Error deleting face:", error);
    }
  };

  const renderUserCircles = () => {
    return faces.map((face, i) => (
      <div key={i} className="relative flex items-center justify-center mb-4 mr-4">
        {/* Delete button */}
        <button
          onClick={() => handleDelete(i)}
          className="absolute top-0 right-0 bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs z-10 hover:bg-red-800"
          title="Delete"
        >
          ×
        </button>

        {/* Circle with image*/}
        <div
          onClick={() => handleCircleClick(i)}
          className="w-16 h-16 rounded-full bg-gray-600 flex items-center justify-center cursor-pointer relative"
          style={{
            backgroundImage: face.imageUrl ? `url(${face.imageUrl})` : 'none',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {isEditing[i] ? (
            <input
              type="text"
              value={peopleNames[i] || ''}
              onChange={(e) => handleNameChange(i, e.target.value)}
              onBlur={() => handleAdd(i)}
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
      className={`fixed top-0 right-0 h-full w-64 bg-gray-800 text-white shadow-lg transform transition-transform duration-300 z-50 ${showPanel ? 'translate-x-0' : 'translate-x-full'
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
