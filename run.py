from app import socketio, app
from services.sockets import events_init

events_init(socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True)
