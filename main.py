import cv2
import mediapipe as mp
import numpy as np
import joblib

# Initialize mediapipe pose solution
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Load the pre-trained model
clf = joblib.load('Pre-Trained Models/random_forest_model.pkl')

# Open a video file
video_path = 'Demo.mp4'
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    # Read a frame from the video
    ret, frame = cap.read()

    if not ret:
        break

    # Resize frame so we can accommodate it on our screen
    frame = cv2.resize(frame, (600, 400))

    # Do Pose detection
    results = pose.process(frame)

    # Draw the detected pose on the original frame
    if results.pose_landmarks is not None:
        # Create a data structure to save the landmarks
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])

        # Convert landmarks to NumPy ndarray and reshape it
        landmarks_arr = np.array(landmarks).reshape(1, -1)

        # Ensure the landmarks array has the same number of features as X
        landmarks_arr = landmarks_arr[:, :132]

        # Make predictions on the landmarks
        predictions = clf.predict(landmarks_arr)

        # Determine the color for the pose skeleton
        skeleton_color = (0, 255, 0) if predictions[0] % 2 != 0 else (0, 0, 255)

        # Draw the pose skeleton and outcome text on the frame with the determined color
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                               mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2),
                               mp_draw.DrawingSpec(color=skeleton_color, thickness=2))

        outcome_text = "Outcome: {}".format(predictions[0])
        cv2.putText(frame, outcome_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Pose Estimation", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
