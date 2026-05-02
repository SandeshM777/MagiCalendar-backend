import os
import json
from google import genai
from PIL import Image
from ics import Calendar, Event
from dotenv import load_dotenv
import datetime
import io

load_dotenv()  # Load environment variables from .env file

# Grab the key securely
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Google GenAI Client
client = genai.Client(api_key=API_KEY)

def process_calendar_image(image_bytes: bytes) -> str:
    # Use io.BytesIO to pretend the raw memory is a saved file
    sample_calendar = Image.open(io.BytesIO(image_bytes))
    
    current_date = datetime.datetime.now().strftime("%B %Y")
    
    prompt = f"""
    You are an expert data extraction tool. Analyze this image of a calendar. 
    Extract all the events you can find.

    CRITICAL CONTEXT: Today's current month and year is {current_date}. 
    If the calendar image does not explicitly state a month or year, assume the dates belong to {current_date}.

    Return the result ONLY as a valid JSON array of objects. 
    Each object must have exactly these keys:
    - "title": (string) A short description of the event.
    - "begin": (string) The exact start date and time in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Use 24-hour time. If no time is specified, default to 09:00:00.

    Do not include any other conversational text or markdown blocks.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[sample_calendar, prompt],
        config={"response_mime_type": "application/json"}
    )

    # Clean and parse JSON
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    events_data = json.loads(clean_json)
    
    # Build Calendar
    cal = Calendar()
    for item in events_data:
        e = Event()
        e.name = item.get("title", "Untitled Event")
        e.begin = item.get("begin")
        cal.events.add(e)
        
    # INSTEAD of saving a file, we return the raw text of the .ics file!
    return cal.serialize()