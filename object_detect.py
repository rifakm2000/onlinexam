import cv2
import torch
import numpy as np
import pyautogui
import datetime
import json
import os
from collections import deque
from ultralytics import YOLO

class ExamProctor:
    def __init__(self):
        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Load YOLOv5 model (updated to 'u' variant)
        self.yolo_model = YOLO("yolov5su.pt").to(self.device)

        # Ensure OpenCV face detection model files exist
        self.face_proto = "deploy.prototxt"
        self.face_model = "res10_300x300_ssd_iter_140000.caffemodel"
        
        if not (os.path.exists(self.face_proto) and os.path.exists(self.face_model)):
            raise FileNotFoundError("Face detection model files are missing!")

        # Load OpenCV face detection model
        self.face_net = cv2.dnn.readNetFromCaffe(self.face_proto, self.face_model)

        # Prohibited objects (as per COCO classes)
        self.PROHIBITED_ITEMS = ["cell phone", "book", "laptop", "tablet", "keyboard", "mouse"]

        # Violation tracking
        self.violations = []
        self.face_detection_history = deque(maxlen=30)
        self.multiple_faces_count = 0
        self.no_face_count = 0
        self.object_violation_count = {}

        # Create directory for screenshots
        self.screenshot_dir = "violation_screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def detect_faces(self, frame):
        """Detect faces using OpenCV's deep learning model."""
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.face_net.setInput(blob)
        detections = self.face_net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array(
                    [frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]]
                )
                faces.append(box.astype("int"))

        return faces

    def detect_objects(self, frame):
        """Detect prohibited objects using YOLOv5."""
        results = self.yolo_model(frame)  # Run detection

        detected_objects = []
        for result in results:
            for box, cls_id, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                class_name = self.yolo_model.names[int(cls_id)]
                if class_name in self.PROHIBITED_ITEMS and conf > 0.5:
                    detected_objects.append({
                        "class": class_name,
                        "box": box.cpu().numpy(),
                        "confidence": float(conf)
                    })

        return detected_objects

    def capture_screen(self):
        """Capture screenshot when violation is detected."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"violation_{timestamp}.png")
        pyautogui.screenshot().save(filename)
        print(f"Screenshot saved: {filename}")

    def log_violation(self, violation_type, details):
        """Log violations in a JSON file."""
        violation = {
            "type": violation_type,
            "details": details,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.violations.append(violation)

        # Save to log file
        with open("violations_log.json", "w") as f:
            json.dump(self.violations, f, indent=4)

    def process_frame(self, frame):
        """Process a single frame for face and object detection."""
        faces = self.detect_faces(frame)
        num_faces = len(faces)
        self.face_detection_history.append(num_faces)

        # Draw bounding boxes around faces
        for face in faces:
            x1, y1, x2, y2 = face
            color = (0, 255, 0) if num_faces == 1 else (0, 0, 255)  # Green for 1 face, Red for multiple
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Violation checks
        if num_faces > 1:
            self.multiple_faces_count += 1
            if self.multiple_faces_count > 5:  # Threshold
                print("⚠️ Multiple faces detected!")
                self.log_violation("multiple_faces", f"Detected {num_faces} faces")
                self.capture_screen()
        else:
            self.multiple_faces_count = 0

        if num_faces == 0:
            self.no_face_count += 1
            if self.no_face_count > 5:
                print("⚠️ No face detected!")
                self.log_violation("no_face", "No face detected in frame")
                self.capture_screen()
        else:
            self.no_face_count = 0

        # Detect prohibited objects
        detected_objects = self.detect_objects(frame)
        for obj in detected_objects:
            class_name = obj["class"]
            box = obj["box"]
            confidence = obj["confidence"]
            cv2.rectangle(
                frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2
            )
            cv2.putText(
                frame,
                f"{class_name}: {confidence:.2f}",
                (int(box[0]), int(box[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )
            print(f"⚠️ Prohibited object detected: {class_name}")
            self.log_violation("prohibited_item", f"Detected {class_name}")
            self.capture_screen()

        return frame


    def start_proctoring(self):
        """Start proctoring with webcam feed."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Webcam not accessible")
            return

        print("📹 Proctoring started... Press 'q' to exit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame (avoid threading for real-time speed)
            frame = self.process_frame(frame)

            # Display output
            cv2.imshow("Proctoring", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    proctor = ExamProctor()
    proctor.start_proctoring()
