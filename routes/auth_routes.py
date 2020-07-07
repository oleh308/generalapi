from resources.auth import SignupApi, LoginApi, ConfirmApi, SignupMentorApi

def auth_routes(api):
    api.add_resource(ConfirmApi, '/confirm')
    api.add_resource(LoginApi, '/api/auth/login')
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(SignupMentorApi, '/api/auth/mentor/signup')
