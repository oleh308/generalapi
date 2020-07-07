from resources.reset_password import ForgotPassword, ResetPassword

def password_routes(api):
    api.add_resource(ForgotPassword, '/api/auth/forgot')
    api.add_resource(ResetPassword, '/api/auth/reset')
