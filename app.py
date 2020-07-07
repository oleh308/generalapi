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
from flask_socketio import SocketIO, join_room, leave_room, emit

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploads')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config.from_envvar('ENV_FILE_LOCATION')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CSRF_ENABLED'] = True

CORS(app)
mail = Mail(app)
from routes import initialize_routes

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

# from app import app
# from flask_socketio import SocketIO, join_room, leave_room, emit
#
# socketio = SocketIO(app, cors_allowed_origins="*")
#
# @socketio.on('chat_init')
# def handle_message(chat):
#     join_room('chat' + chat['id'])
#     print('joined chat: ' + 'chat' + chat['id'])
#
# @socketio.on('chat_deinit')
# def handle_message(chat):
#     leave_room('chat' + chat['id'])
#     print('left chat: ' + 'chat' + chat['id'])
#
# @socketio.on('connect')
# def connect():
#     print('Connection init')
#
# if __name__ == '__main__':
#     socketio.run(app, debug=True)
