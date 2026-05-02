from fastapi import FastAPI, UploadFile, File
import uvicorn
from ai_service import process_calendar_image

# Initialize the server
app = FastAPI(title="Magicalendar API")

# A simple "health check" endpoint to make sure the server is awake
@app.get("/")
def read_root():
    return {"status": "online", "message": "Magicalendar Server is running!"}

# The main endpoint your mobile app will hit
@app.post("/api/v1/scan")
async def scan_calendar(file: UploadFile = File(...)):
    # 1. We receive the image file from the phone here
    print(f"Received file: {file.filename}")
    
    try:
        # 1. Read the raw image bytes from the uploaded file
        image_bytes = await file.read()
        
        # 2. Pass those bytes to your AI function
        ics_text = process_calendar_image(image_bytes)
        
        # 3. For now, save it locally to prove it worked 
        # (Later, we will email this text instead!)
        with open('api_scanned_calendar.ics', 'w') as f:
            f.writelines(ics_text)
            
        return {
            "status": "success", 
            "message": "Calendar parsed successfully!",
            # We can even return the raw data to the phone if we want
            "data_preview": ics_text[:100] + "..." 
        }
        
    except Exception as error:
        print(f"Error: {error}")
        return {"status": "failed", "message": str(error)}

# This tells Python how to run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)