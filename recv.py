import cv2
import socket
import pickle
import struct
import serial
from math import hypot
from google.protobuf.json_format import MessageToDict
import mediapipe

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

def receive_video_stream(host, port):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    data = b""
    payload_size = struct.calcsize("Q")

    def get_frame():
        nonlocal data
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)  # 4K
            if not packet:
                return None
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame

    return get_frame

def main():
    s = serial.Serial("COM3")
    get_frame = receive_video_stream('192.168.1.2', 9999)  # Replace with the sender's IP address

    hand_model = initialise_hand_detector()
    while True:
        frame = get_frame()
        if frame is not None:
            overlay_image = process_frame(hand_model, frame, s)
            cv2.imshow("Camera", overlay_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
