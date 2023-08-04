from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class Photo(db.Model):
	__tablename__ = 'photos'

	id = db.Column(db.Integer, primary_key=True)
	photo_id = db.Column(db.String(64), index=True, unique=True)
	url = db.Column(db.String(1024))

	def __repr__(self):
		return '<Photo {}>'.format(self.photo_id)


