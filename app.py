from flask_mail import Mail
from flask_cors import CORS
from flask_restful import Api
from flask_bcrypt import Bcrypt
from os.path import join, dirname, realpath
from flask import Flask, jsonify, flash, request, redirect, url_for
from resources.errors import errors
from database.db import initialize_db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token
)

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploads')


app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CSRF_ENABLED'] = True

CORS(app)
mail = Mail(app)
from resources.routes import initialize_routes

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@jwt.expired_token_loader
def expired_token_callback(expired_token):
    return { 'error': 'Token expired', 'type': 'tokenExpired' }, 401

@jwt.invalid_token_loader
def invalid_token_callback(expired_token):
    return { 'error': 'Token invalid', 'type': 'tokenInvalid' }, 401

@jwt.unauthorized_loader
def unauthorized_callback(expired_token):
    return { 'error': 'noToken', 'type': 'tokenMissing' }, 401


initialize_db(app)
initialize_routes(api)
