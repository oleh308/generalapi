from app import socketio, app
from flask_socketio import join_room, leave_room, emit

@socketio.on('chat_init')
def handle_message(chat):
    join_room('chat' + chat['id'])
    print('joined chat: ' + 'chat' + chat['id'])

@socketio.on('chat_deinit')
def handle_message(chat):
    leave_room('chat' + chat['id'])
    print('left chat: ' + 'chat' + chat['id'])

@socketio.on('connect')
def connect():
    print('Connection init')

@socketio.on('disconnect')
def connect():
    print('Disconnection deinit')


if __name__ == '__main__':
    socketio.run(app, debug=True)
