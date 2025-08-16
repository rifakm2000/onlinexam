class WebExamProctor {
    constructor(referenceImage, options = {}) {
        this.referenceImage = referenceImage;
        this.options = {
            faceDetectionThreshold: 10,
            lookingAwayThreshold: 15,
            matchThreshold: 50,
            captureInterval: 1000,
            ...options
        };
        
        this.violations = [];
        this.noFaceCount = 0;
        this.lookingAwayCount = 0;
        this.lastMatchConfidence = 0;
        this.isProcessing = false;
    }

    async initialize() {
        // Load face-api.js models
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
            faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
            faceapi.nets.faceRecognitionNet.loadFromUri('/models')
        ]);

        // Get reference face descriptor
        this.referenceDescriptor = await this.getFaceDescriptor(this.referenceImage);
    }

    async getFaceDescriptor(imageElement) {
        const detection = await faceapi
            .detectSingleFace(imageElement, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceDescriptor();
            
        return detection ? detection.descriptor : null;
    }

    async processFrame(videoElement) {
        if (this.isProcessing) return null;
        this.isProcessing = true;

        try {
            // Detect face in current frame
            const detection = await faceapi
                .detectSingleFace(videoElement, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceDescriptor();

            if (!detection) {
                this.noFaceCount++;
                if (this.noFaceCount > this.options.faceDetectionThreshold) {
                    this.logViolation('no_face', 'No face detected in frame');
                }
                return {
                    status: 'no_face',
                    confidence: 0
                };
            }

            this.noFaceCount = 0;

            // Compare with reference face
            if (this.referenceDescriptor) {
                const distance = faceapi.euclideanDistance(
                    detection.descriptor,
                    this.referenceDescriptor
                );
                
                // Convert distance to confidence score (0-100)
                const confidence = Math.max(0, 100 * (1 - distance));
                this.lastMatchConfidence = confidence;

                if (confidence < this.options.matchThreshold) {
                    this.logViolation('face_mismatch', `Face mismatch detected (confidence: ${confidence.toFixed(1)}%)`);
                    return {
                        status: 'mismatch',
                        confidence
                    };
                }

                // Check if looking away using landmarks
                const landmarks = detection.landmarks;
                const isLookingAway = this.detectLookingAway(landmarks);
                
                if (isLookingAway) {
                    this.lookingAwayCount++;
                    if (this.lookingAwayCount > this.options.lookingAwayThreshold) {
                        this.logViolation('looking_away', 'Student looking away from screen');
                        return {
                            status: 'looking_away',
                            confidence
                        };
                    }
                } else {
                    this.lookingAwayCount = 0;
                }

                return {
                    status: 'match',
                    confidence
                };
            }

            return {
                status: 'error',
                message: 'Reference descriptor not available'
            };

        } finally {
            this.isProcessing = false;
        }
    }

    detectLookingAway(landmarks) {
        const nose = landmarks.getNose();
        const leftEye = landmarks.getLeftEye();
        const rightEye = landmarks.getRightEye();
        
        // Calculate face center and nose deviation
        const faceCenterX = (leftEye[0].x + rightEye[3].x) / 2;
        const deviation = Math.abs(nose[3].x - faceCenterX);
        
        // Normalize by face width
        const faceWidth = rightEye[3].x - leftEye[0].x;
        return (deviation / faceWidth) > 0.2;
    }

    logViolation(type, details) {
        const violation = {
            timestamp: new Date().toISOString(),
            type,
            details
        };
        this.violations.push(violation);

        // Dispatch violation event
        const event = new CustomEvent('proctoring-violation', {
            detail: violation
        });
        window.dispatchEvent(event);
    }

    getViolations() {
        return this.violations;
    }

    getLastMatchConfidence() {
        return this.lastMatchConfidence;
    }
}