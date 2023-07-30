from flask import Flask, render_template, Response
import subprocess

app = Flask(__name__)

def read_frame(process):
    image_data = b''
    while True:
        data = process.stdout.read(1)
        if not data:
            break
        image_data += data
        if image_data[-2:] == b'\xff\xd9':
            # End of a JPEG image
            break
    return image_data

def video_feed():
    # Change the '1' in '-i 1' to the correct index of your USB camera
    command = "ffmpeg -f avfoundation -framerate 10 -i 1 -vcodec mjpeg -"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    while True:
        frame = read_frame(process)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed_route():
    return Response(video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')  # Create an HTML template file named 'index.html' in the same directory

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

