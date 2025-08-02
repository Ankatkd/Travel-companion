import React from 'react';
import { auth } from '../firebase'; // Assuming firebase is correctly set up
import { signOut } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';

// Navbar now accepts onFindRoute (a function) and showFindRoute (a boolean) as props
const Navbar = ({ onFindRoute, showFindRoute }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await signOut(auth);
      alert("Logged out successfully!");
      navigate("/"); // Redirect to login page after logout
    } catch (error) {
      console.error("Logout error:", error);
      alert("Failed to log out. Please try again.");
    }
  };

  return (
    <nav className="bg-gradient-to-r from-blue-700 to-purple-800 p-4 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        <div className="text-white text-2xl font-bold">
          Travel Companion AI
        </div>
        <div className="flex items-center space-x-4"> {/* Use flex to space buttons */}
          {/* Conditionally render the "Get Directions" button */}
          {showFindRoute && (
            <button
              onClick={onFindRoute}
              className="bg-green-500 text-white px-4 py-2 rounded-md font-semibold hover:bg-green-600 transition duration-200 ease-in-out"
            >
              Get Directions
            </button>
          )}
          <button
            onClick={handleLogout}
            className="bg-white text-blue-700 px-4 py-2 rounded-md font-semibold hover:bg-blue-100 transition duration-200 ease-in-out"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;