# travel-companion-backend/utils/gemini_travel_planner.py

import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

def get_gemini_travel_details(selected_places: list, start_location: str):
    """
    Generates a detailed travel plan using Gemini, ordering places for optimal travel,
    and including the user's starting point.

    Args:
        selected_places (list): A list of dictionaries, each representing a selected
                                tourist place with details like 'title', 'address',
                                'latitude', 'longitude', 'summary', 'image', etc.
        start_location (str): The user's starting address for the day.

    Returns:
        dict: A dictionary containing the structured travel plan or an error message.
    """
    model_name = "gemini-1.5-flash"

    # Format the selected places into a readable string for the prompt
    places_info = []
    for i, place in enumerate(selected_places):
        # Ensure all required keys exist, providing defaults if missing
        title = place.get('title', f"Place {i+1}")
        address = place.get('address', 'N/A')
        latitude = place.get('latitude', 'N/A')
        longitude = place.get('longitude', 'N/A')
        summary = place.get('summary', 'No summary available.')
        main_attraction = place.get('main_attraction', 'N/A')
        best_time_to_visit = place.get('best_time_to_visit', 'N/A')
        visiting_hours = place.get('visiting_hours', 'N/A')

        places_info.append(
            f"  - Title: {title}\n"
            f"    Address: {address}\n"
            f"    Coordinates: ({latitude}, {longitude})\n"
            f"    Summary: {summary}\n"
            f"    Main Attraction: {main_attraction}\n"
            f"    Best Time to Visit: {best_time_to_visit}\n"
            f"    Visiting Hours: {visiting_hours}"
        )
    
    places_list_str = "\n".join(places_info)

    prompt = f"""
    You are an expert travel planner. Create a detailed daily itinerary for a user who wants to visit the following tourist attractions.

    **User's Starting Location for the day:** {start_location}

    **Selected Tourist Attractions (with details):**
    {places_list_str}

    **Instructions:**
    1.  **Optimize the Route:** Arrange all places, starting from the user's '{start_location}', in a logical order to minimize travel time and maximize efficiency. Assume typical city traffic and public transport/taxi availability.
    2.  **Time Allocation:** Suggest a reasonable time to spend at each attraction.
    3.  **Travel Between Places:** For each segment between attractions (including from the starting location to the first attraction), estimate the travel time and suggest a suitable mode of transport (e.g., walk, taxi, metro, bus).
    4.  **Morning Start:** Assume the day starts at approximately 9:00 AM from the '{start_location}'.
    5.  **Meal Breaks:** Incorporate a lunch break (approx. 1 hour) and suggest a good time for it.
    6.  **Structure:** Provide the plan as a JSON array of daily activities. Each activity object should have the following structure:
        - `time_slot`: String (e.g., "9:00 AM - 9:30 AM", "1:00 PM - 2:00 PM")
        - `activity`: String (e.g., "Travel from [Previous Place] to [Current Place]", "Visit [Attraction Name]", "Lunch break")
        - `location`: String (e.g., "Starting from Home/Hotel", "Gateway of India", "Local Restaurant")
        - `details`: String (e.g., "Estimated travel time: 30 minutes by taxi.", "Explore the monument and nearby area.", "Enjoy local cuisine.")
        - `type`: String (e.g., "travel", "attraction", "meal")

    **Example of desired JSON format:**
    ```json
    [
      {{
        "time_slot": "9:00 AM - 9:30 AM",
        "activity": "Travel from User's Starting Location to Gateway of India",
        "location": "{start_location} to Gateway of India",
        "details": "Estimated travel time: 30 minutes by taxi/ride-share.",
        "type": "travel"
      }},
      {{
        "time_slot": "9:30 AM - 11:00 AM",
        "activity": "Visit Gateway of India",
        "location": "Gateway of India, Mumbai",
        "details": "Explore the iconic monument, take photos, and learn about its history. Allow time for crowds.",
        "type": "attraction"
      }},
      {{
        "time_slot": "11:00 AM - 11:20 AM",
        "activity": "Travel from Gateway of India to Colaba Causeway",
        "location": "Gateway of India to Colaba Causeway",
        "details": "Estimated travel time: 10-20 minutes walk.",
        "type": "travel"
      }},
      {{
        "time_slot": "11:20 AM - 1:00 PM",
        "activity": "Explore Colaba Causeway",
        "location": "Colaba Causeway, Mumbai",
        "details": "Enjoy shopping for souvenirs, clothes, and handicrafts. Experience the bustling street market.",
        "type": "attraction"
      }},
      {{
        "time_slot": "1:00 PM - 2:00 PM",
        "activity": "Lunch Break",
        "location": "Leopold Cafe or nearby restaurant in Colaba",
        "details": "Savor local and international cuisine. Consider trying seafood.",
        "type": "meal"
      }}
      // ... continue for all selected places and travel back to a reasonable end point
    ]
    ```
    """

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        raw_response_text = ""
        for part in response.parts:
            if part.text:
                raw_response_text += part.text

        cleaned_response_text = raw_response_text.strip()
        
        # Remove Markdown code block if present
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]

        # Attempt to parse the JSON
        try:
            travel_plan = json.loads(cleaned_response_text)
            if not isinstance(travel_plan, list):
                print(f"Warning: Gemini did not return a JSON array for travel plan. Raw: {cleaned_response_text}")
                return {"error": "Failed to generate valid travel plan: Malformed JSON output from Gemini (not an array)."}
            return travel_plan
        except json.JSONDecodeError as e:
            print(f"JSON decoding error for travel plan: {e}. Raw response: {cleaned_response_text}")
            return {"error": f"Failed to generate valid travel plan: JSON parsing error - {e}. Raw output: {cleaned_response_text}"}

    except Exception as e:
        print(f"Error calling Gemini API for travel details: {e}")
        return {"error": f"Failed to generate travel plan: {e}"}