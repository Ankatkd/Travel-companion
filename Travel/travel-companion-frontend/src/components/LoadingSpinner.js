// src/components/LoadingSpinner.js
import React from 'react';

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-500"></div>
      <p className="mt-4 text-lg text-blue-600">{message}</p>
    </div>
  );
};

export default LoadingSpinner;