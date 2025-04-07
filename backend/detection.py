import cv2
from ultralytics import YOLO
import os

model = YOLO('yolov8n.pt')

def process_image(img):
    results = model(img)
    
    organic = 0
    inorganic = 0
    detections = {}
    
    for result in results:
        for box in result.boxes:
            cls = int(box.cls)
            label = model.names[cls]
            
            if label in ["apple", "banana", "leaf"]:
                organic += 1
            else:
                inorganic += 1
            
            detections[label] = detections.get(label, 0) + 1
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(img, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
    
    # Format detections as "count - label" pairs
    detection_string = ", ".join([f"{count} - {label}" 
                                for label, count in detections.items()])
    
    total = organic + inorganic
    organic_percentage = round((organic / total) * 100, 2) if total > 0 else 0
    inorganic_percentage = round((inorganic / total) * 100, 2) if total > 0 else 0
    
    processed_path = os.path.join("processed_images", f"result_{os.urandom(4).hex()}.jpg")
    cv2.imwrite(processed_path, img)
    
    return {
        "organic": organic,
        "inorganic": inorganic,
        "organic_percentage": organic_percentage,
        "inorganic_percentage": inorganic_percentage,
        "processed_image_path": processed_path,
        "detections": detection_string
    }