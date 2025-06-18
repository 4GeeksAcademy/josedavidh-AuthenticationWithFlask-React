"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException, send_email
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

api = Blueprint('api', __name__)

# manejo de hash de contraseña
def set_password(password, salt):
    return generate_password_hash(f"{password}{salt}")

def check_password(pass_hash, password, salt):
    return check_password_hash(pass_hash, f"{password}{salt}")

# final manejo de hash de contraseña
expires_in_minutes = 15
expires_delta = timedelta(minutes=expires_in_minutes)

# Allow CORS requests to this API
CORS(api)


@api.route('/health-check', methods=['GET'])
def handle_hello():
    

    return jsonify("ok"), 200

@api.route('/signup', methods=['POST'])
def add_user():
    data = request.json
    email = data.get("email", None)
    fullname = data.get("fullname", None)
    password = data.get("password", None)
    salt = b64encode(os.urandom(32)).decode("utf-8")
 

    if email is None or fullname is None or password is None:
        return jsonify("You must provide email, fullname, and password"), 400
    
    # existing_user = User.query.filter_by(email=email).one_or_none()
    # if existing_user:
    #     return jsonify("Email is already registered"), 400
    
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
    else:
        # Consulta si el email existe
        user = User.query.filter_by(email=email).one_or_none()
        if user is None:
            return jsonify({"message": "The user is not registered"}), 400
        else:
            if check_password(user.password, password, user.salt):
                # Se genera el token
                token = create_access_token(identity=str(user.id))

                return jsonify({
                    "token": token
                }), 200
            else:
                return jsonify({ "message": "Incorrect password" }), 400
            
@api.route("/user", methods=["GET"])
@jwt_required()
def get_all_users():
    users = User.query.all()

    return jsonify(list(map(lambda item: item.serialize(), users))), 200

@api.route("/me", methods=["GET"])
@jwt_required() # Procesamiento de consultas con token únicamente
def get_a_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user is None:
        return jsonify("Invalid email or password"), 404
    return jsonify(user.serialize())

@api.route("/reset-password", methods=["POST"])
def reset_password():
    # Requerimiento del correo electrónico para enviar el enlace de recuperación
    body = request.json
    # user = User.query.filter_by(email = body).one_or_one() --> Former
    user = User.query.filter_by(email=body.get("email")).one_or_none()
    if user is None:
        return jsonify("Invalid email or password"), 404
    # access_token = create_access_token(
    #    identity=body, expires_delta=expires_delta) --> former
    access_token = create_access_token(
        identity=body.get("email"), expires_delta=expires_delta)

    message = f"""
        <a href="{os.getenv("FRONTEND_URL")}/password-update?token={access_token}">Recuperar contraseña</a>
    """

    data = {
        "subject": "Recuperación de contraseña",
        # "to": body, --> Former
        "to": body.get("email"),
        "message": message
    }

    email_sent = send_email(
        data.get("subject"), data.get("to"), data.get("message")
    )

    if email_sent:
        return jsonify("Message sent"), 200
    else:
        return jsonify("Error"), 200
    
@api.route("/update-password", methods=["PUT"])
@jwt_required()
def update_password():
    user_token_email = get_jwt_identity()
    # password = request.json --> Former
    password = request.json.get("password")

    user = User.query.filter_by(email=user_token_email).first()

    if user is not None:
        salt = b64encode(os.urandom(32)).decode("utf-8")
        password = set_password(password, salt)

        user.salt = salt
        user.password = password

        try:
            db.session.commit()
            return jsonify("password changed successfully"), 201
        except Exception as error:
            db.session.rollback()
            return jsonify("Error"), 500
        
        print(user.serialize)
