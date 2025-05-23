import React, { useState } from 'react';

const Dropdown = () => {
  const [selectedMethod, setSelectedMethod] = useState('');

  const handleChange = (event) => {
    setSelectedMethod(event.target.value);
    // You can handle what happens when an option is selected
    console.log(`Selected: ${event.target.value}`);
  };

  return (
    <div className="flex justify-center items-center p-2">
      <div className="relative">
        <select
          value={selectedMethod}
          onChange={handleChange}
          className="block w-full p-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="" disabled>Select Model</option>
          <option value="query_rag">Basic Model</option>
          <option value="query_memory">Advanced Model</option>
        </select>

        {/* Optional: display selected option */}
        {selectedMethod && (
          <div className="mt-2 text-blue-700">
            <p>You selected: {selectedMethod}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dropdown;
