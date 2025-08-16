import cv2
import numpy as np
import time
import datetime
import os
import argparse
import threading

class YOLOv3ProctorSystem:
    def __init__(self, 
                 confidence_threshold=0.5,
                 nms_threshold=0.4,
                 report_dir="violation_reports",
                 weights_path="yolov3.weights",
                 config_path="yolov3.cfg",
                 classes_path="coco.names"):
        
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.report_dir = report_dir
        self.violation_count = 0
        self.last_violation_time = None
        self.cooldown_period = 10  # seconds between reports
        
        # Create directory for storing violation reports if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        
        # Load YOLO model
        self.net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        
        # Set preferred backend and target
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # Use cv2.dnn.DNN_TARGET_CUDA for GPU
        
        # Load class names
        with open(classes_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # List of objects that may indicate violations during an exam
        self.violation_objects = [
            'cell phone', 'laptop', 'book', 'tvmonitor', 'remote',
            'keyboard', 'mouse', 'person'  # person is to detect multiple people
        ]
        
        # Get output layer names
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        # Start the webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
            
        # Set up the window
        cv2.namedWindow("Exam Proctoring System (YOLOv3)", cv2.WINDOW_NORMAL)
        
        # Store multiple person detection
        self.person_count = 0
    
    def detect_objects(self, frame):
        height, width, _ = frame.shape
        
        # Preprocess image for YOLO
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        
        # Set input and forward pass
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)
        
        # Information to return
        class_ids = []
        confidences = []
        boxes = []
        
        # Process detections
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        
        # Count persons for multiple person detection
        self.person_count = sum(1 for i in range(len(class_ids)) if self.classes[class_ids[i]] == 'person' and i in indexes)
        
        detected_objects = []
        for i in range(len(boxes)):
            if i in indexes:
                label = self.classes[class_ids[i]]
                confidence = confidences[i]
                detected_objects.append((label, confidence, boxes[i]))
        
        return detected_objects
    
    def check_violations(self, detected_objects):
        violations = []
        
        # Check for prohibited objects
        for label, confidence, box in detected_objects:
            if label in self.violation_objects:
                # Special case for 'person': only consider it a violation if more than one person is detected
                if label == 'person' and self.person_count <= 1:
                    continue
                violations.append((label, confidence, box))
        
        return violations
    
    def log_violation(self, frame, violations):
        """Save evidence of the violation with a timestamp"""
        now = datetime.datetime.now()
        
        # Only log if we're outside the cooldown period
        if (self.last_violation_time is None or 
            (now - self.last_violation_time).total_seconds() > self.cooldown_period):
            
            self.violation_count += 1
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(self.report_dir, f"violation_{timestamp}.jpg")
            cv2.imwrite(report_path, frame)
            
            # Create text report
            text_report = os.path.join(self.report_dir, f"violation_{timestamp}.txt")
            with open(text_report, "w") as f:
                f.write(f"Violation Report #{self.violation_count}\n")
                f.write(f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Detected violations:\n")
                for label, confidence, _ in violations:
                    f.write(f"- {label}: {confidence:.2f} confidence\n")
                if self.person_count > 1:
                    f.write(f"- Multiple persons detected: {self.person_count}\n")
            
            self.last_violation_time = now
            return True
        
        return False
    
    def run(self):
        print("Starting YOLOv3 exam proctoring system...")
        print("Press 'q' to quit")
        
        frame_count = 0
        start_time = time.time()
        fps = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            frame_count += 1
            
            # Process every 15 frames to improve performance
            if frame_count % 15 == 0:
                detected_objects = self.detect_objects(frame)
                violations = self.check_violations(detected_objects)
                
                # Draw boxes for all detected objects
                for label, confidence, box in detected_objects:
                    x, y, w, h = box
                    
                    # Use red color for violations, green for allowed objects
                    color = (0, 0, 255) if any(v[0] == label for v in violations) else (0, 255, 0)
                    
                    # Draw rectangle and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    text = f"{label}: {confidence:.2f}"
                    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Handle violations
                if violations:
                    # Draw a red border around the entire frame to indicate violation
                    h, w = frame.shape[:2]
                    cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 20)
                    
                    # Add violation warning text
                    cv2.putText(frame, "VIOLATION DETECTED", (int(w/2) - 150, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    
                    # Log the violation
                    if self.log_violation(frame, violations):
                        violation_text = ", ".join([v[0] for v in violations])
                        if self.person_count > 1:
                            violation_text += f", multiple persons ({self.person_count})"
                        print(f"Violation detected and logged! Items: {violation_text}")
            
            # Display info about detected persons
            person_text = f"Persons detected: {self.person_count}"
            cv2.putText(frame, person_text, (10, frame.shape[0] - 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Calculate FPS
            if frame_count % 10 == 0:
                end_time = time.time()
                fps = 10 / (end_time - start_time)
                start_time = end_time
            
            # Display FPS
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, frame.shape[0] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display the proctoring status
            status = "Status: Monitoring..."
            cv2.putText(frame, status, (frame.shape[1] - 300, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show the frame
            cv2.imshow("Exam Proctoring System (YOLOv3)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

def download_yolo_files():
    """Download YOLOv3 weights, config, and class names if not already present"""
    import urllib.request
    
    files = {
        "yolov3.weights": "https://pjreddie.com/media/files/yolov3.weights",
        "yolov3.cfg": "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg",
        "coco.names": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
    }
    
    for filename, url in files.items():
        if not os.path.exists(filename):
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
            print(f"Downloaded {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Exam Proctoring System with YOLOv3')
    parser.add_argument('--confidence', type=float, default=0.5,
                        help='Confidence threshold for object detection (default: 0.5)')
    parser.add_argument('--nms', type=float, default=0.4,
                        help='Non-maximum suppression threshold (default: 0.4)')
    parser.add_argument('--report_dir', type=str, default='violation_reports',
                        help='Directory to store violation reports (default: violation_reports)')
    parser.add_argument('--weights', type=str, default='yolov3.weights',
                        help='Path to YOLOv3 weights file (default: yolov3.weights)')
    parser.add_argument('--config', type=str, default='yolov3.cfg',
                        help='Path to YOLOv3 config file (default: yolov3.cfg)')
    parser.add_argument('--classes', type=str, default='coco.names',
                        help='Path to class names file (default: coco.names)')
    args = parser.parse_args()
    
    # Download YOLOv3 files if they don't exist
    download_yolo_files()
    
    # Create and run the proctoring system
    proctor = YOLOv3ProctorSystem(
        confidence_threshold=args.confidence,
        nms_threshold=args.nms,
        report_dir=args.report_dir,
        weights_path=args.weights,
        config_path=args.config,
        classes_path=args.classes
    )
    proctor.run()