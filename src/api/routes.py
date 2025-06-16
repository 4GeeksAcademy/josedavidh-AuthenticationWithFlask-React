"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode
import os

api = Blueprint('api', __name__)

# manejo de hash de contraseña

def set_password(password, salt):
    return generate_password_hash(f"{password}{salt}")

def check_password(pass_hash, password):
    return check_password_hash(pass_hash, password)

# final manejo de hash de contraseña

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route('/signup', methods=['POST'])
def add_user():
    data = request.json
    email = data.get("email", None)
    fullname = data.get("fullname", None)
    password = data.get("password", None)
    salt = b64encode(os.urandom(32)).decode("utf-8")
 

    if email is None or fullname is None or password is None:
        return jsonify("You must provide email, fullname, and password"), 400
    
    user = User()
    user.email = email
    user.fullname = fullname
    user.password = set_password(password, salt)
    user.salt = salt

    db.session.add(user)

    try:
        db.session.commit()
        return jsonify("User created successfully"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}"), 500
    
@api.route('/login', methods=["POST"])
def user_login():
    data = request.json
    email = data.get("email", None)
    password = data.get("password", None)

    if email is None or password is None:
        return jsonify("You must provide email and password"), 400

    print(data)

    return jsonify("trabajando por mi nuevo pais"), 201