from flask import Flask, render_template, Response 
import cv2

app = Flask(__name__)

def video_feed():
    cap = cv2.VideoCapture(0) 

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b' --frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
@app.route('/video_feed') 
def video_feed_route():
    return Response(video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')  # Create an HTML template file named 'index.html' in the same directory

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)  # Set the desired host and port
