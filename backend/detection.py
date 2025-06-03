import cv2
from ultralytics import YOLO
import os
import numpy as np

# Initialize model
model = YOLO(r'C:\Users\aslin\OneDrive\Desktop\PROJECT_YOLO\yolo\runs\detect\train3\weights\best.pt')

def process_image(img):
    """Process image to detect multiple waste objects individually."""
    try:
        # Input handling
        if isinstance(img, str):
            if not os.path.exists(img):
                raise FileNotFoundError(f"Image file not found: {img}")
            img = cv2.imread(img)
            if img is None:
                raise ValueError(f"Failed to read image: {img}")

        # Model prediction with optimized settings for multi-object detection
        results = model.predict(
            img,
            conf=0.3,  # Lower confidence threshold to detect smaller objects
            iou=0.3,   # NMS threshold to avoid duplicate detections
            imgsz=640   # Match training size
        )
        
        organic = 0
        inorganic = 0
        detections = []
        detection_counts = {"Organic": 0, "Inorganic": 0}

        for result in results:
            for box in result.boxes:
                cls = int(box.cls)
                label = model.names[cls]
                conf = float(box.conf)
                
                # Update counts
                if label.lower() == "organic":
                    organic += 1
                    detection_counts["Organic"] += 1
                    color = (0, 255, 0)  # Green for organic
                else:
                    inorganic += 1
                    detection_counts["Inorganic"] += 1
                    color = (0, 0, 255)  # Red for inorganic

                # Store detection details
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "position": [x1, y1, x2, y2]
                })
                
                # Draw bounding boxes with improved visibility
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    img, 
                    f"{label} {conf:.2f}",
                    (x1, max(y1-10, 20)),  # Keep text in frame
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    (255, 255, 255),  # White text
                    2,
                    cv2.LINE_AA
                )

        # Calculate percentages
        total = organic + inorganic
        organic_percentage = round((organic / max(total, 1)) * 100, 2)
        inorganic_percentage = round((inorganic / max(total, 1)) * 100, 2)

        # Save processed image
        os.makedirs("processed_images", exist_ok=True)
        processed_path = os.path.join("processed_images", f"result_{os.urandom(4).hex()}.jpg")
        cv2.imwrite(processed_path, img)

        # Format detection string
        detection_string = ", ".join([f"{count}x {label}" for label, count in detection_counts.items() if count > 0])

        return {
            "organic": organic,
            "inorganic": inorganic,
            "organic_percentage": organic_percentage,
            "inorganic_percentage": inorganic_percentage,
            "processed_image_path": processed_path.replace("\\", "/"),
            "detections": detection_string,
            "detailed_detections": detections,  # New: contains all detection details
            "success": True,
            "total_objects": total
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "organic": 0,
            "inorganic": 0,
            "organic_percentage": 0,
            "inorganic_percentage": 0,
            "detections": "No detections",
            "detailed_detections": []
        }