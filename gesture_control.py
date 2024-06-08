import cv2
import mediapipe
from math import hypot
from google.protobuf.json_format import MessageToDict
import serial

def initialise_hand_detector():
    mpHands = mediapipe.solutions.hands
    hand_model = mpHands.Hands(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75,
        max_num_hands=2
    )
    return hand_model

def process_frame(hand_model, frame, s):
    flip = cv2.flip(frame, 1)
    results = hand_model.process(cv2.cvtColor(flip, cv2.COLOR_BGR2RGB))
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            label = MessageToDict(results.multi_handedness[i])['classification'][0]['label']
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

            height, width, _ = flip.shape
            pixel_landmarks = [(int(lm[0] * width), int(lm[1] * height)) for lm in landmarks]
            
            for point in pixel_landmarks:
                flip = cv2.circle(flip, point, 3, (255, 0, 0), 1)
            thumb_tip = pixel_landmarks[4]
            index_tip = pixel_landmarks[8]
            L = hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])

            if label == "Left":
                print("left: ", L)
                s.write(b"Hello")
            elif label == "Right":
                print("right", L)
    return flip

def main():
    s = serial.Serial("COM3")

    cap = cv2.VideoCapture(0)
    hand_model = initialise_hand_detector()
    while True:
        valid, frame = cap.read()
        if valid:
            overlay_image = process_frame(hand_model, frame, s)
            cv2.imshow("Camera", overlay_image)

        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
main()