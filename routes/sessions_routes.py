from resources.session import SessionApi, SessionsApi, SessionJoinApi, SessionLeaveApi

def sessions_routes(api):
    api.add_resource(SessionsApi, '/api/sessions')
    api.add_resource(SessionApi, '/api/sessions/<id>')
    api.add_resource(SessionJoinApi, '/api/sessions/<id>/join')
    api.add_resource(SessionLeaveApi, '/api/sessions/<id>/leave')
