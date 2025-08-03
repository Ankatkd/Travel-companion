// src/pages/HomePage.js

import React, { useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import axios from "axios";
import LoadingSpinner from "../components/LoadingSpinner";
import CustomAlert from "../components/CustomAlert";
import TravelBreakdown from "../components/TravelBreakdown";
import { getApiBase } from "../apiBase";

function HomePage() {
  const [location, setLocation] = useState("");
  const [startLocation, setStartLocation] = useState("");
  const [optimizationPreference, setOptimizationPreference] = useState("fastest");
  const [places, setPlaces] = useState([]);
  const [selectedPlaces, setSelectedPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [travelPlan, setTravelPlan] = useState(null);
  const baseUrl = getApiBase();
  const handleSearch = async () => {
    if (!location.trim()) {
      setError("Please enter a location to search.");
      return;
    }
    setLoading(true);
    setError(null);
    setPlaces([]);
    setSelectedPlaces([]);
    setTravelPlan(null);
    try {
      const res = await axios.post(`${baseUrl}/api/suggest`, {
        address: location,
      });
      if (res.data.places && res.data.places.length > 0) {
        setPlaces(res.data.places);
        // Automatically set the start location to the search location for convenience
        setStartLocation(location);
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
      const placeExists = prevSelectedPlaces.some((p) => p.title === place.title);
      if (placeExists) {
        return prevSelectedPlaces.filter((p) => p.title !== place.title);
      } else {
        return [...prevSelectedPlaces, place];
      }
    });
  };

  const getTravelDetails = useCallback(async () => {
    if (selectedPlaces.length < 2) {
      setError("Please select at least 2 places to get a travel breakdown.");
      return;
    }
    if (!startLocation.trim()) {
      setError("Please enter your starting location.");
      return;
    }

    setLoading(true);
    setError(null);
    setTravelPlan(null);

    // --- Frontend logic to simulate route optimization based on user preference ---
    let optimizedPlaces = [...selectedPlaces];
    // In a real-world scenario, the backend would handle the complex
    // shortest path or TSP-like algorithm based on this preference.
    // Here, we'll just demonstrate the data flow by logging the preference.
    console.log(`User wants to optimize for: ${optimizationPreference}`);
    console.log(`Starting from: ${startLocation}`);
    // Your backend API would take startLocation and optimizationPreference
    // and return the travel plan with the places in the optimal order.
    // For now, we'll simply pass the selected places as is.

    try {
      const res = await axios.post(`${baseUrl}/api/get-travel-details`, {
        selectedPlaces: optimizedPlaces,
        startLocation: startLocation, // Pass the user's specific starting location
        optimizationPreference: optimizationPreference, // Pass the optimization choice
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
  }, [selectedPlaces, startLocation, optimizationPreference]);

  return (
    <div className="min-h-screen bg-gray-50 font-inter">
      <Navbar onFindRoute={getTravelDetails} showFindRoute={selectedPlaces.length > 0} />
      
      <div className="max-w-4xl mx-auto mt-10 p-8 bg-white rounded-2xl shadow-xl border border-gray-200">
        <h2 className="text-3xl font-extrabold text-gray-900 mb-6 text-center">
          Discover Your Next Adventure 🌍
        </h2>
        <div className="flex flex-col md:flex-row gap-4 items-center mb-4">
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter a city to find attractions (e.g., Mumbai, Paris)"
            className="flex-1 w-full md:w-auto px-5 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-lg"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
          <button
            onClick={handleSearch}
            className="w-full md:w-auto bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700 transition duration-300 ease-in-out font-semibold shadow-md"
          >
            Search
          </button>
        </div>
        
        {/* New input for user's starting point */}
        <div className="flex flex-col md:flex-row gap-4 items-center">
          <input
            type="text"
            value={startLocation}
            onChange={(e) => setStartLocation(e.target.value)}
            placeholder="Enter your starting point (e.g., Your Home Address, Airport)"
            className="flex-1 w-full md:w-auto px-5 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 text-lg"
          />
        </div>

        {loading && <LoadingSpinner message="Finding amazing places for you..." />}
        {error && <CustomAlert message={error} />}
      </div>
      
      {/* Optimization Preference Selection */}
      {selectedPlaces.length > 1 && (
        <div className="max-w-4xl mx-auto my-8 p-6 bg-white rounded-2xl shadow-xl border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Optimize your route
          </h3>
          <div className="flex gap-6">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="radio"
                name="optimization"
                value="fastest"
                checked={optimizationPreference === "fastest"}
                onChange={() => setOptimizationPreference("fastest")}
                className="form-radio h-5 w-5 text-indigo-600 border-gray-300 focus:ring-indigo-500"
              />
              <span className="text-gray-700 font-medium">Fastest Route 🚀</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="radio"
                name="optimization"
                value="cheapest"
                checked={optimizationPreference === "cheapest"}
                onChange={() => setOptimizationPreference("cheapest")}
                className="form-radio h-5 w-5 text-indigo-600 border-gray-300 focus:ring-indigo-500"
              />
              <span className="text-gray-700 font-medium">Cheapest Route 💸</span>
            </label>
          </div>
        </div>
      )}

      {/* Travel Plan (moved to appear before the list of places) */}
      {travelPlan && (
        <TravelBreakdown
          travelOptions={travelPlan.travelOptions}
          selectedPlaces={selectedPlaces}
        />
      )}

      {places.length > 0 && (
        <div className="max-w-6xl mx-auto mt-12 px-4 pb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {places.map((place, index) => {
              const isPlaceSelected = selectedPlaces.some(
                (p) => p.title === place.title
              );
              return (
                <div
                  key={index}
                  className={`bg-white rounded-2xl p-6 relative flex flex-col h-full shadow-lg transition-all duration-300 ease-in-out transform hover:scale-[1.02] ${
                    isPlaceSelected ? 'ring-4 ring-blue-500' : ''
                  }`}
                >
                  <div className="relative">
                    <img
                      src={place.image}
                      alt={place.title}
                      className="w-full h-48 object-cover rounded-xl mb-4 shadow-sm"
                      onError={(e) =>
                        (e.target.src =
                          "https://placehold.co/300x200/e0e7ff/3f51b5?text=No+Image+Found")
                      }
                    />
                    <input
                      type="checkbox"
                      className="absolute top-3 left-3 h-6 w-6 accent-blue-600 cursor-pointer"
                      onChange={() => handleCheckboxChange(place)}
                      checked={isPlaceSelected}
                    />
                  </div>
                  <h3 className="font-bold text-2xl mt-2 text-gray-900 leading-tight">{place.title}</h3>
                  <p className="text-base text-gray-700 mt-2 flex-grow">{place.summary}</p>
                  <div className="mt-4 text-sm text-gray-800 space-y-2">
                    <p>
                      <strong className="font-semibold text-gray-900">Best Time:</strong> {place.best_time_to_visit}
                    </p>
                    <p>
                      <strong className="font-semibold text-gray-900">Visiting Hours:</strong> {place.visiting_hours}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;
