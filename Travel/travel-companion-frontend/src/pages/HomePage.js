// src/pages/HomePage.js
import React, { useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import axios from "axios";
import LoadingSpinner from "../components/LoadingSpinner";
import CustomAlert from "../components/CustomAlert";
import TravelBreakdown from "../components/TravelBreakdown"; // NEW IMPORT

function HomePage() {
  const [location, setLocation] = useState("");
  const [places, setPlaces] = useState([]);
  const [selectedPlaces, setSelectedPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [travelPlan, setTravelPlan] = useState(null); // NEW state for travel plan

  const handleSearch = async () => {
    if (!location.trim()) {
      setError("Please enter a location to search.");
      return;
    }
    setLoading(true);
    setError(null);
    setPlaces([]);
    setSelectedPlaces([]); // Clear selected places on new search
    setTravelPlan(null); // Clear previous travel plan
    try {
      const res = await axios.post("http://localhost:8086/api/suggest", {
        address: location,
      });
      if (res.data.places && res.data.places.length > 0) {
        setPlaces(res.data.places);
      } else {
        setError("No famous historical or scenic tourist places found for this location. Please try a different search or be more specific.");
      }
    } catch (err) {
      console.error("Error fetching tourist places:", err);
      setError("Failed to fetch tourist places. Please check your network connection or try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (place) => {
    setSelectedPlaces((prevSelectedPlaces) => {
      if (prevSelectedPlaces.includes(place)) {
        return prevSelectedPlaces.filter((p) => p !== place);
      } else {
        return [...prevSelectedPlaces, place];
      }
    });
  };

  // Renamed and repurposed from openRoute to getTravelDetails
  const getTravelDetails = useCallback(async () => {
    if (selectedPlaces.length < 2) {
      setError("Please select at least 2 places to get a travel breakdown.");
      return;
    }

    setLoading(true);
    setError(null);
    setTravelPlan(null); // Clear previous plan
    try {
      // Send the selected places (including their coordinates) to the backend
      const res = await axios.post("http://localhost:8086/api/get-travel-details", {
        selectedPlaces: selectedPlaces.map(p => ({
          title: p.title,
          address: p.address,
          latitude: p.latitude,
          longitude: p.longitude,
        })),
      });
      
      if (res.data && res.data.travelOptions) {
        setTravelPlan(res.data);
      } else {
        setError("Failed to get travel breakdown. No options found.");
      }

    } catch (err) {
      console.error("Error fetching travel details:", err);
      setError(`Failed to get travel breakdown: ${err.response?.data?.detail || err.message}. Please try again.`);
    } finally {
      setLoading(false);
    }
  }, [selectedPlaces]); // Dependency array includes selectedPlaces

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Pass the new function to Navbar, and show it if places are selected */}
      <Navbar onFindRoute={getTravelDetails} showFindRoute={selectedPlaces.length > 0} />
      <div className="max-w-4xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4">
          Discover Famous Tourist Attractions 🌍
        </h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter a city or location (e.g., Mumbai, Paris)"
            className="flex-1 border rounded px-4 py-2 focus:ring-blue-500 focus:border-blue-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition duration-200 ease-in-out"
          >
            Search
          </button>
        </div>

        {loading && <LoadingSpinner message="Finding amazing places for you..." />}
        {error && <CustomAlert message={error} />}
      </div>

      {places.length > 0 && (
        <div className="max-w-6xl mx-auto mt-8 px-4 pb-10">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {places.map((place, index) => (
              <div
                key={index}
                className="bg-white shadow-md rounded-lg p-4 relative flex flex-col h-full"
              >
                <img
                    src={place.image}
                    alt={place.title}
                    className="w-full h-48 object-cover rounded mb-3"
                    onError={(e) =>
                    (e.target.src =
                       "[https://placehold.co/300x200?text=No+Image+Found](https://placehold.co/300x200?text=No+Image+Found)")
                    }
                  />
                <input
                  type="checkbox"
                  className="absolute top-3 left-3 h-5 w-5 accent-blue-500"
                  onChange={() => handleCheckboxChange(place)}
                  checked={selectedPlaces.includes(place)}
                />
                <h3 className="font-bold text-xl mt-2 text-gray-900">{place.title}</h3>
                <p className="text-sm text-gray-700 mt-1 flex-grow">{place.summary}</p>
                <div className="mt-3 text-sm text-gray-800 space-y-1">
                  <p><strong>Specialty:</strong> {place.main_attraction}</p>
                  <p><strong>Best Time to Visit:</strong> {place.best_time_to_visit}</p>
                  <p><strong>Visiting Hours:</strong> {place.visiting_hours}</p>
                  <p><strong>Address:</strong> {place.address}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Render the TravelBreakdown component if travelPlan exists */}
      {travelPlan && <TravelBreakdown travelPlan={travelPlan} />}
    </div>
  );
}

export default HomePage;