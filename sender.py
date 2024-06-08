import cv2
import socket
import pickle
import struct

def send_video(host, port=9999):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    connection = client_socket.makefile('wb')

    # Open the webcam
    cam = cv2.VideoCapture(0)

    try:
        while cam.isOpened():
            ret, frame = cam.read()
            if not ret:
                break

            # Serialize the frame
            data = pickle.dumps(frame)
            # Pack the frame size first, then the frame data
            message = struct.pack("Q", len(data)) + data

            # Send the frame
            client_socket.sendall(message)

            # Display the frame locally
            cv2.imshow('Sending Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cam.release()
        client_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    send_video('192.168.1.2', 9999)  # Replace with the receiver's IP address and port
