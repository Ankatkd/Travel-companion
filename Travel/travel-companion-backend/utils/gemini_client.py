# travel-companion-backend/utils/gemini_client.py

import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import requests
import re # Added for cleaning Gemini's JSON response if needed
from utils.geocode_utils import get_coordinates_from_address # Import geocoding utility

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- search_pixabay_image function ---
def search_pixabay_image(query: str) -> str:
    """
    Searches Pixabay for a high-quality image of a given query and returns its direct URL.
    Returns a specific error placeholder string if no image is found or an API error occurs.
    """
    pixabay_api_key = os.getenv("PIXABAY_API_KEY")
    if not pixabay_api_key:
        print("Error: PIXABAY_API_KEY not found in .env.")
        return "https://placehold.co/300x200?text=No+Pixabay+API+Key"

    search_url = "https://pixabay.com/api/"
    params = {
        "key": pixabay_api_key,
        "q": query.replace(" ", "+"),   # Pixabay uses '+' for spaces in query
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": 3,   # Get a few results to pick from
        "safesearch": True
    }
    try:
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()   # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        if data and data['hits']:
            # Pixabay returns multiple sizes; 'webformatURL' is usually a good general-purpose size.
            print(f"Found Pixabay image for '{query}': {data['hits'][0]['webformatURL']}")
            return data['hits'][0]['webformatURL']
        else:
            print(f"No Pixabay image found for query: '{query}'")
            return "https://placehold.co/300x200?text=No+Pixabay+Found"
    except requests.exceptions.RequestException as e:
        print(f"Error searching Pixabay for '{query}': {e}")
        return "https://placehold.co/300x200?text=Pixabay+Search+Error"
    except Exception as e:
        print(f"An unexpected error occurred during Pixabay search for '{query}': {e}")
        return "https://placehold.co/300x200?text=Error"


# --- search_unsplash_image function ---
def search_unsplash_image(query: str) -> str:
    """
    Searches Unsplash for a high-quality image of a given query and returns its direct URL.
    Returns a specific error placeholder string if no image is found or an API error occurs.
    """
    unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not unsplash_access_key:
        return "https://placehold.co/300x200?text=No+Unsplash+API+Key"

    search_url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query + " tourist attraction", # Added " tourist attraction" for better relevance
        "orientation": "landscape",
        "per_page": 1,
        "client_id": unsplash_access_key
    }
    try:
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()   # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        if data and data['results']:
            print(f"Found Unsplash image for '{query}': {data['results'][0]['urls']['regular']}")
            return data['results'][0]['urls']['regular']
        else:
            print(f"No Unsplash image found for query: '{query}'")
            return "https://placehold.co/300x200?text=No+Unsplash+Found"
    except requests.exceptions.RequestException as e:
        print(f"Error searching Unsplash for '{query}': {e}")
        return "https://placehold.co/300x200?text=Unsplash+Search+Error"
    except Exception as e:
        print(f"An unexpected error occurred during Unsplash search for '{query}': {e}")
        return "https://placehold.co/300x200?text=Error"


def suggest_tourist_places(location: str):
    """
    Suggests famous historical and scenic tourist attractions for a given location
    using the Gemini API and external image search tools (Pixabay and Unsplash),
    and then fetches coordinates for each place using OpenCage.
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in .env. Please set it.")
        return []

    model_name = "gemini-1.5-flash"

    # Define tool schemas - ONLY Pixabay and Unsplash are declared
    unsplash_tool_declaration = {
        "name": "search_unsplash_image",
        "description": "Searches Unsplash for a high-quality, general scenic or public domain image and returns its direct URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The general term to search for on Unsplash (e.g., 'city park', 'mountain view', 'local market')."},
            },
            "required": ["query"],
        },
    }

    pixabay_tool_declaration = {
        "name": "search_pixabay_image",
        "description": "Searches Pixabay for a high-quality, general scenic or public domain image and returns its direct URL. This is the primary tool for finding images for tourist attractions and scenic spots.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The general term to search for on Pixabay (e.g., 'city park', 'mountain view', 'local market')."},
            },
            "required": ["query"],
        },
    }

    tool_definitions = {
        "function_declarations": [
            pixabay_tool_declaration,   # Pixabay is declared first as the primary
            unsplash_tool_declaration   # Unsplash is declared as the fallback option
        ]
    }

    # Prompt for Gemini model to generate tourist place suggestions with tool calls
    prompt = f"""
    Suggest 6 top and most famous **historical and scenic tourist attractions** in {location}.
    Prioritize places that are well-known landmarks, historically significant, or offer unique natural beauty.

    For each of the 6 suggested places, provide the following details in a comprehensive and engaging manner:
    - title
    - summary (what it is, a concise description)
    - main_attraction (why it's famous, its main attraction, historical significance, or unique specialty)
    - best_time_to_visit (e.g., month range, time of day)
    - visiting_hours (e.g., daily schedule, closed days)
    - address (as precise as possible, including street, city, state, country)
    - **image**: For this field, you MUST use one of the available tools to get a relevant image URL.
      - **Always prioritize `search_pixabay_image` for finding high-quality images for all types of tourist places (historical landmarks, scenic spots, etc.).** The query should be a descriptive phrase (e.g., "Shaniwar Wada Pune", "Parvati Hill Pune", "Elephanta Caves").
      - **Only if `search_pixabay_image` is unlikely to find a good relevant image, then use `search_unsplash_image`.** The query should be a descriptive phrase.

      The value for 'image' should be a JSON object representing the tool call, like this:
      {{ "call": {{ "function": "TOOL_NAME", "args": {{ "query": "Your Query" }} }} }}

    Return the result as a valid JSON array of dictionaries. Ensure all keys are present, and values are strings. If a specific piece of information is genuinely unknown or not applicable, use "N/A" for its value.

    Example of expected JSON format with tool calls:
    [
      {{
        "title": "Gateway of India",
        "summary": "An iconic arch monument built in the 20th century in Mumbai, India, symbolizing the city's historical gateway.",
        "main_attraction": "Its grand Indo-Saracenic architecture, historical significance as a former entry point to India, and its prime location offering views of the Arabian Sea and Elephanta Caves ferries.",
        "best_time_to_visit": "November to March for pleasant weather; early mornings or late afternoons to avoid crowds and enjoy the light.",
        "visiting_hours": "Open 24 hours (monument exterior); ferry services typically 7:00 AM - 5:30 PM.",
        "address": "Apollo Bunder, Colaba, Mumbai, Maharashtra 400001, India",
        "image": {{ "call": {{ "function": "search_pixabay_image", "args": {{ "query": "Gateway of India Mumbai" }} }} }}
      }},
      {{
        "title": "Marine Drive",
        "summary": "A 3.6-kilometer long C-shaped boulevard along the Arabian Sea, often called the 'Queen's Necklace' due to its streetlights at night.",
        "main_attraction": "Its stunning panoramic sea views, especially at sunset, the vibrant atmosphere with locals and tourists, and its iconic 'Queen's Necklace' illumination.",
        "best_time_to_visit": "Evening for sunset views and cooler breeze; during high tide for dramatic waves.",
        "visiting_hours": "Open 24 hours.",
        "address": "Netaji Subhash Chandra Bose Road, Mumbai, Maharashtra, India",
        "image": {{ "call": {{ "function": "search_pixabay_image", "args": {{ "query": "Marine Drive Mumbai" }} }} }}
      }}
    ]
    """

    try:
        model = genai.GenerativeModel(model_name, tools=tool_definitions)
        response = model.generate_content(prompt)
        
        raw_response_text = ""
        # Aggregate text from all parts of the response
        for part in response.parts:
            if part.text:
                raw_response_text += part.text

        response_text = raw_response_text.strip()
        print(f"Gemini ({model_name}) raw response (with tool call structure):\n", response_text)

        # Clean up Markdown code block if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        places_with_tool_calls = json.loads(response_text)
        
        final_places = []
        for place in places_with_tool_calls:
            # 1. Handle Image Fetching
            actual_image_url = "https://placehold.co/300x200?text=Image+Not+Found" # Default fallback
            if "image" in place and isinstance(place["image"], dict) and "call" in place["image"]:
                tool_call_dict = place["image"]["call"]
                function_name = tool_call_dict.get("function")
                image_query = tool_call_dict.get("args", {}).get("query")

                if function_name == "search_pixabay_image" and image_query:
                    print(f"Attempting Pixabay search for '{image_query}'...")
                    temp_url = search_pixabay_image(image_query)
                    
                    # If Pixabay failed, try Unsplash
                    if "No Pixabay" in temp_url or "Pixabay Search Error" in temp_url or "Pixabay API Key" in temp_url or "Error" in temp_url:
                        print(f"Pixabay failed for '{image_query}'. Attempting Unsplash fallback...")
                        temp_url = search_unsplash_image(image_query)
                    
                    actual_image_url = temp_url
                    
                elif function_name == "search_unsplash_image" and image_query:
                    print(f"Attempting Unsplash search for '{image_query}' (Gemini chose Unsplash directly)...")
                    actual_image_url = search_unsplash_image(image_query)
                else:
                    print(f"Warning: Unknown or malformed tool call: {tool_call_dict}. Using default placeholder for image.")

                # Final check: if actual_image_url still contains an error message, replace it
                if "No Pixabay" in actual_image_url or \
                   "Pixabay Search Error" in actual_image_url or \
                   "No Unsplash" in actual_image_url or \
                   "Unsplash Search Error" in actual_image_url or \
                   "Tool Error" in actual_image_url or \
                   "No Unsplash API Key" in actual_image_url or \
                   "No Pixabay API Key" in actual_image_url or \
                   "Error" in actual_image_url:
                    print(f"All automated image searches failed for '{image_query}'. Using generic placeholder.")
                    actual_image_url = "https://placehold.co/300x200?text=Image+Unavailable"
                
                place["image"] = actual_image_url
            else:
                print(f"No valid image tool call found for {place.get('title')}. Using default placeholder.")
                place["image"] = actual_image_url # Assign default if no tool call was suggested

            # 2. Handle Coordinate Fetching using geocode_utils
            place_address = place.get("address")
            if place_address:
                print(f"Attempting to geocode address for '{place.get('title')}': '{place_address}'")
                coords = get_coordinates_from_address(place_address)
                if coords:
                    place["latitude"] = coords["lat"]
                    place["longitude"] = coords["lng"]
                    print(f"Successfully geocoded '{place.get('title')}': Lat={coords['lat']}, Lng={coords['lng']}")
                else:
                    print(f"Could not geocode address for '{place.get('title')}'. Setting latitude/longitude to None.")
                    place["latitude"] = None
                    place["longitude"] = None
            else:
                print(f"No address provided for '{place.get('title')}', cannot geocode. Setting latitude/longitude to None.")
                place["latitude"] = None
                place["longitude"] = None

            # Only add place if it has a title and an image, and ideally coordinates
            # Although we set to None, the frontend expects float, so we might need a filter later if we strictly need coords
            # For now, let's include all as the frontend can handle null/missing coords.
            final_places.append(place)
        
        return final_places if isinstance(final_places, list) else []

    except json.JSONDecodeError as e:
        print(f"JSON decoding error from Gemini response: {e}")
        print(f"Problematic response text: '{response_text}'")
        return []
    except Exception as e:
        print("Gemini API call or processing error:", e)
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Gemini response text before error: {response.text}")
        return []