import React from "react";

const CustomAlert = ({ message }) => {
  return (
    <div className="mt-4 p-4 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-md">
      {message}
    </div>
  );
};

export default CustomAlert;
