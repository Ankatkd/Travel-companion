import React from "react";

function TravelBreakdown({ travelOptions, selectedPlaces }) {
  /**
   * Checks if a travel option's location matches any of the selected places.
   * This is used to apply a different style to the selected destinations.
   * @param {object} travelOption The travel option object from the Gemini API.
   * @returns {boolean} True if the travel option's location is in the selectedPlaces array, false otherwise.
   */
  const isSelected = (travelOption) => {
    return selectedPlaces.some((place) =>
      travelOption.location.includes(place.title)
    );
  };

  return (
    <div className="max-w-4xl mx-auto my-8 p-8 bg-white rounded-2xl shadow-xl border border-gray-200 transform transition-transform duration-300">
      <h2 className="text-3xl font-extrabold text-gray-900 mb-6 text-center border-b-2 border-indigo-300 pb-4">
        Your Personalized Travel Itinerary
      </h2>
      <div className="space-y-6">
        {travelOptions && travelOptions.length > 0 ? (
          travelOptions.map((option, index) => (
            <div
              key={index}
              className={`p-6 rounded-xl shadow-lg transition-all duration-300 ease-in-out cursor-pointer hover:shadow-xl hover:-translate-y-1 ${
                isSelected(option)
                  ? "bg-indigo-50 border-l-8 border-indigo-500 transform scale-105"
                  : "bg-gray-50 border-l-4 border-gray-200"
              }`}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white text-2xl font-bold mr-4
                bg-indigo-500 shadow-md">
                  {/* Using emojis for visual distinction based on the activity type */}
                  {option.type === "travel" && (
                    <span role="img" aria-label="travel-icon">✈️</span>
                  )}
                  {option.type === "attraction" && (
                    <span role="img" aria-label="attraction-icon">📍</span>
                  )}
                  {option.type === "meal" && (
                    <span role="img" aria-label="meal-icon">🍽️</span>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                      {option.time_slot}
                    </p>
                    <p className={`text-xs font-bold px-3 py-1 rounded-full ${
                      option.type === "travel" ? "bg-indigo-200 text-indigo-800" :
                      option.type === "attraction" ? "bg-emerald-200 text-emerald-800" :
                      "bg-amber-200 text-amber-800"
                    }`}>
                      {option.type}
                    </p>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 leading-tight">
                    {option.activity}
                  </h3>
                  <p className="text-gray-700 mt-2 text-base">{option.details}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500 py-10">
            Generating travel plan...
          </p>
        )}
      </div>
    </div>
  );
}

export default TravelBreakdown;
