from resources.interest import InterestsApi, InterestApi

def interests_routes(api):
    api.add_resource(InterestsApi, '/api/interests')
    api.add_resource(InterestApi, '/api/interests/<id>')
