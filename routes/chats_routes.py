from resources.chat import ChatsApi, ChatApi, JoinPublicApi, \
    JoinPrivateApi, MessagesApi, LeaveApi, PromoteApi, RemoveApi, ChatSessionsApi, ChatActionApi, ChatActionsApi

def chats_routes(api):
    api.add_resource(ChatsApi, '/api/chats')
    api.add_resource(ChatApi, '/api/chats/<id>')
    api.add_resource(JoinPublicApi, '/api/chats/public/join/<host_id>')
    api.add_resource(JoinPrivateApi, '/api/chats/private/join/<host_id>')
    api.add_resource(LeaveApi, '/api/chats/leave/<id>')
    api.add_resource(PromoteApi, '/api/chats/promote/<id>')
    api.add_resource(MessagesApi, '/api/chats/messages/<id>')
    api.add_resource(RemoveApi, '/api/chats/remove/<id>')
    api.add_resource(ChatSessionsApi, '/api/chats/<id>/sessions')
    api.add_resource(ChatActionsApi, '/api/chats/<id>/actions')
    api.add_resource(ChatActionApi, '/api/chats/<id>/actions/<action_id>')
