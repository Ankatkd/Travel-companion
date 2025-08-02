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
You are an expert travel planner. Your task is to create a detailed daily itinerary for a user who wants to visit a list of tourist attractions, starting from a specific location.

**User's Starting Location for the day:** {start_location}

**Selected Tourist Attractions:**
{places_list_str}

**Instructions:**
1. **Optimize the Route:** Arrange all places, starting from the user's '{start_location}', in a logical order to minimize travel time.
2. **Detailed Plan:** Assume the day starts at 9:00 AM. For each segment of the journey, including visits and travel, suggest a time slot, activity, location, details, and the type of activity.
3. **Meal Breaks:** Incorporate a lunch break (approx. 1 hour) around midday.
4. **Output Format:** Provide the plan as a single JSON object. The object must have one key, `travelOptions`, which contains a detailed daily itinerary as a JSON array. Each element in this array must be an object with the following keys: `time_slot`, `activity`, `location`, `details`, and `type`.
5. **No Extra Text:** Only output the JSON object. Do not include any conversational text or markdown code block delimiters (like ```json).

**Desired JSON Format (Example):**
```json
{{
  "travelOptions": [
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
      "details": "Explore the iconic monument and nearby area. Allow time for crowds.",
      "type": "attraction"
    }},
    {{
      "time_slot": "1:00 PM - 2:00 PM",
      "activity": "Lunch Break",
      "location": "Leopold Cafe or nearby restaurant in Colaba",
      "details": "Savor local and international cuisine.",
      "type": "meal"
    }}
  ]
}}
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
        
        # In this updated prompt, we explicitly ask Gemini not to include markdown,
        # so this cleaning step is less necessary but still a good safeguard.
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]

        # Attempt to parse the JSON
        try:
            travel_plan = json.loads(cleaned_response_text)
            
            # The key change: return the entire JSON object, which should contain 'travelOptions'
            # as per the updated prompt.
            return travel_plan
            
        except json.JSONDecodeError as e:
            print(f"JSON decoding error for travel plan: {e}. Raw response: {cleaned_response_text}")
            return {"error": f"Failed to generate valid travel plan: JSON parsing error - {e}. Raw output: {cleaned_response_text}"}

    except Exception as e:
        print(f"Error calling Gemini API for travel details: {e}")
        return {"error": f"Failed to generate travel plan: {e}"}
