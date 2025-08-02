import React from "react";

const TouristPlaces = ({ places }) => {
  if (!places || places.length === 0) {
    return (
      <p className="text-center text-gray-500 mt-6">
        Your results will appear here.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {places.map((place, index) => (
        <div
          key={index}
          className="bg-white shadow-lg rounded-lg overflow-hidden hover:shadow-xl transition duration-300"
        >
          <img
            src={place.image || "https://via.placeholder.com/400x250?text=No+Image"}
            alt={place.title}
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h2 className="text-lg font-bold text-gray-800">{place.title}</h2>
            <p className="text-sm text-gray-600 mt-2">{place.summary}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TouristPlaces;