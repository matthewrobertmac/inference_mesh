from flask import Flask, render_template, Response
import subprocess

app = Flask(__name__)

def video_feed():
    command = 'fswebcam --no-banner -r 640x480 -'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    while True:
        frame = process.stdout.read(640 * 480 * 3)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed_route():
    return Response(video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')  # Create an HTML template file named 'index.html' in the same directory

