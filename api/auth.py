
from flask import request
from flask_jwt_extended import create_access_token
from database.db_config import config_db
from security.iam_services import IAMService
from security.password_hasher import PasswordHasher
from utils.api_response import api_response
from analytics.logger import setup_logger

from . import api_bp

iam = IAMService(config_db)
log = setup_logger()

@api_bp.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()
        if not data:
            return api_response(False, error="JSON body required", status=400)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return api_response(False, error="Username and password required", status=400)

        user = iam.get_user(username)
        if not user or user.get("active") != 1:
            return api_response(False, error="Invalid credentials", status=401)

        hasher = PasswordHasher()
        if not hasher.verify_password(user["password_hash"], password):
            return api_response(False, error="Invalid credentials", status=401)

        token = create_access_token(identity=username)
        return api_response(data={"access_token": token})

    except Exception as e:
        log.error(f"Login error: {e}")
        return api_response(False, error="Internal error", status=500)
