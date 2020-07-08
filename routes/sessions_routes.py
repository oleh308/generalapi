from resources.session import SessionApi, SessionsApi

def sessions_routes(api):
    api.add_resource(SessionsApi, '/api/sessions')
    api.add_resource(SessionApi, '/api/sessions/<id>')
