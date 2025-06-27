import React from 'react';

const DropDownMenu = ({ selectedMethod, setSelectedMethod, disabled = false }) => {
  const handleChange = (event) => {
    const value = event.target.value;
    setSelectedMethod(value);
    console.log(`Selected method: ${value}`);
  };

  return (
    <div className="flex justify-center items-center p-2">
      <div className="relative w-full max-w-xs">
        <select
          value={selectedMethod}
          onChange={handleChange}
          disabled={disabled}
          className={`block w-full p-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
            disabled ? 'opacity-50 cursor-not-allowed' : ''
          } ${
            selectedMethod === '' ? 'text-gray-400' : 'text-gray-700'
          }`}
        >
          <option value="" disabled className="text-gray-400">
            Select Model
          </option>
          <option value="rag" className="text-gray-700">
            Basic Model
          </option>
          <option value="memory" className="text-gray-700">
            Advanced Model
          </option>
        </select>

        {/* Visual indicator of selected method */}
        {selectedMethod && (
          <div className="mt-1 text-sm text-indigo-600 font-medium">
            Selected: {selectedMethod === 'query_rag' ? 'Basic Model' : 'Advanced Model'}
          </div>
        )}
      </div>
    </div>
  );
};

export default DropDownMenu;