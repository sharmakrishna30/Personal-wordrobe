from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

from utils.image_analysis import analyze_image
from utils.recommendations import get_recommendations

app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class LikedProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product = db.Column(db.String(200), nullable=False)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload_image():
    image = request.files.get('image')
    user_id = request.form.get('user_id')

    if not image or not user_id:
        return jsonify({'error': 'Image and user_id are required'}), 400

    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    attributes = analyze_image(filepath)
    recommendations = get_recommendations(attributes)

    return jsonify({
        'attributes': attributes,
        'recommendations': recommendations
    })

# Like a product
@app.route('/like', methods=['POST'])
def like_product():
    data = request.json
    user_id = data.get('user_id')
    product = data.get('product')

    if not user_id or not product:
        return jsonify({'error': 'user_id and product are required'}), 400

    liked = LikedProduct(user_id=user_id, product=product)
    db.session.add(liked)
    db.session.commit()

    return jsonify({'message': 'Product liked!'})

# Get likes for a user
@app.route('/likes/<int:user_id>', methods=['GET'])
def get_likes(user_id):
    likes = LikedProduct.query.filter_by(user_id=user_id).all()
    return jsonify([like.product for like in likes])

# Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful', 'user_id': user.id})

# Entry point
if _name_ == '_main_':
    db.create_all()
    app.run(debug=True)