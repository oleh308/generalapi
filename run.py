from app import app
from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('connect')
def connect():
    print('Connection init')

if __name__ == '__main__':
    socketio.run(app, debug=True)
