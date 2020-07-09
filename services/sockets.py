from flask_socketio import join_room, leave_room, emit

def events_init(socketio):
    @socketio.on('timeline_init')
    def handle_message(timeline):
        for mentor in timeline['mentors']:
            join_room('mentor' + mentor)

        print('joined timeline: ' + ','.join(timeline['mentors']))

    @socketio.on('timeline_deinit')
    def handle_message(timeline):
        for mentor in timeline['mentors']:
            leave_room('mentor' + mentor)

        print('left timeline: ' + ','.join(timeline['mentors']))

    @socketio.on('chats_init')
    def handle_message(chats):
        for id in chats['ids']:
            join_room('chat' + id)

        print('joined chats: ' + ','.join(chats['ids']))

    @socketio.on('chats_deinit')
    def handle_message(chats):
        for id in chats['ids']:
            leave_room('chat' + id)

        print('left chats: ' + ','.join(chats['ids']))

    @socketio.on('post_init')
    def handle_message(post):
        join_room('post' + post['id'])
        print('joined post: ' + 'post' + post['id'])

    @socketio.on('post_deinit')
    def handle_message(post):
        leave_room('post' + post['id'])
        print('left post: ' + 'post' + post['id'])

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
