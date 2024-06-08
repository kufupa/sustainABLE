import cv2
import socket
import pickle
import struct

def send_video_stream(host, port):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print('Server listening on {}:{}'.format(host, port))

    conn, addr = server_socket.accept()
    print('Connection from:', addr)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set width to 640
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set height to 480

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Compress the frame using JPEG
            result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            conn.sendall(message)

            cv2.imshow('Sending Video', cv2.imdecode(frame, cv2.IMREAD_COLOR))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    send_video_stream('0.0.0.0', 9999)  # Use '0.0.0.0' to listen on all available interfaces
