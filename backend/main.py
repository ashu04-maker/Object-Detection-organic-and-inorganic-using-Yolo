from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from detection import process_image
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from typing import List, Dict
import json

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("processed_images", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Mount static files
app.mount("/processed_images", StaticFiles(directory="processed_images"), name="processed_images")

# History file path
HISTORY_FILE = "data/history.json"

def save_to_history(entry: Dict):
    """Save classification entry to history file"""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        
        history.append(entry)
        
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error saving history: {e}")

def get_history() -> List[Dict]:
    """Get classification history"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
                # Ensure all entries have detections field
                for entry in history:
                    if "detections" not in entry:
                        entry["detections"] = ""
                return history
    except Exception as e:
        print(f"Error loading history: {e}")
    return []

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Read image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Process image
    result = process_image(img)
    processed_image_filename = os.path.basename(result["processed_image_path"])
    
    # Create history entry
    entry = {
        "image": processed_image_filename,
        "organic": result["organic"],
        "organic_percentage": result["organic_percentage"],
        "inorganic": result["inorganic"],
        "inorganic_percentage": result["inorganic_percentage"],
        "detections": result["detections"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    }
    
    # Save to history
    save_to_history(entry)
    
    return entry

@app.delete("/history/{image_name}")
async def delete_history_item(image_name: str):
    try:
        history = get_history()
        updated_history = [item for item in history if item["image"] != image_name]
        
        with open(HISTORY_FILE, "w") as f:
            json.dump(updated_history, f)
            
        return {"status": "success", "message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_classification_history():
    return get_history()