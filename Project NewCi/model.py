# from app import app
# from flask_sqlalchemy import SQLAlchemy

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# class Kecamatan(db.Model):
#     __tablename__ = 'kecamatan'
#     id_kecamatan = db.Column(db.Integer, primary_key=True)
#     nama_kecamatan = db.Column(db.String(100))

# class Kelurahan(db.Model):
#     __tablename__ = 'kelurahan'
#     id_kelurahan = db.Column(db.Integer, primary_key=True)
#     nama_kelurahan = db.Column(db.String(100))
#     id_kecamatan = db.Column(db.Integer, db.ForeignKey('kecamatan.id_kecamatan'))