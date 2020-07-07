from resources.post import PostsApi, PostApi, CommentApi, LikeApi, RecommendationsApi

def posts_routes(api):
    api.add_resource(PostsApi, '/api/posts')
    api.add_resource(PostApi, '/api/posts/<id>')
    api.add_resource(RecommendationsApi, '/api/posts/recommendations')

    # TO UPDATE
    api.add_resource(LikeApi, '/api/posts/<id>/like')

    # TO UPDATE
    api.add_resource(CommentApi, '/api/posts/<id>/comments')
