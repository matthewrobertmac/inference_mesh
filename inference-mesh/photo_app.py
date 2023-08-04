from flask import Flask, jsonify, request 
from flask_cors import CORS

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE URI'] = 'sqlite:///photos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)

@app.route('/photos', methods=['GET']) 
def get_photos():
	photos = Photo.query.all()
	return jsonify([photo.url for photo in photos]) 

@app.route('/photos', methods=['POST'])
def add_photo():
	photo_id = request.json.get('photo_id')
	url = request.json.get('url')
	photo = Photo(photo_id=photo_id, url=url)
	db.session.add(photo)
	db.session.commit()
	return jsonify({'photo_id': photo.photo_id, 'url': photo.url}) 

