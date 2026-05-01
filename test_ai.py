import os
import json
from google import genai
from PIL import Image
from ics import Calendar, Event
from dotenv import load_dotenv
import datetime

load_dotenv()  # Load environment variables from .env file

# Grab the key securely
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Google GenAI Client
client = genai.Client(api_key=API_KEY)

# Load the sample image
image_path = "Backend/calendar-example.jpg" 
try:
    sample_calendar = Image.open(image_path)
except FileNotFoundError:
    print(f"Error: I couldn't find '{image_path}'. Make sure it's in the same folder as this script!")
    exit()

current_date = datetime.datetime.now().strftime("%B %Y") # e.g., "May 2026"

# The Prompt Engineering. This is how we force the AI to act like an API instead of a chatbot.
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

print("Sending image to Gemini... (this might take a few seconds)")

# Make the API Call to Gemini (gemini-2.5-flash is latest, fastes for images)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[sample_calendar, prompt],
    config={
        # This config tells the model we strictly want JSON back
        "response_mime_type": "application/json", 
    }
)

print("Received JSON. Building ICS file...")

# Convert JSON to ICS
try:
    # Clean the text (in case Gemini added markdown ticks)
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    
    # Convert string to Python List/Dictionary
    events_data = json.loads(clean_json)
    
    # Create a new Calendar
    cal = Calendar()
    
    # Loop through the data and create events
    for item in events_data:
        e = Event()
        e.name = item.get("title", "Untitled Event")
        e.begin = item.get("begin")
        cal.events.add(e)
        
    # Save it to an .ics file
    with open('my_scanned_calendar.ics', 'w') as f:
        f.writelines(cal.serialize())
        
    print("\nSUCCESS! Open your folder and double-click 'my_scanned_calendar.ics'!")

except Exception as error:
    print("\nError parsing JSON or building Calendar:")
    print(error)
    print("Raw Output was:", response.text)