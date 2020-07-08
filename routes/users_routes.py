from resources.user import UserApi, MentorApi, UserImageApi, \
    FollowApi, UserProductsApi

def users_routes(api):
    # FRONT END UPDATE
    api.add_resource(UserApi, '/api/users/<id>')
    api.add_resource(FollowApi, '/api/users/follow/<id>')
    # FRONT END UPDATE
    api.add_resource(UserImageApi, '/api/users/image/<id>')
    api.add_resource(MentorApi, '/api/users/<id>/mentor')
    api.add_resource(UserProductsApi, '/api/users/<user_id>/products')
