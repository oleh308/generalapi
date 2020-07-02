from .movie import MoviesApi, MovieApi
from .interest import InterestsApi, InterestApi
from .country import CountriesApi, CountryApi
from .auth import SignupApi, LoginApi, ConfirmApi, SignupMentorApi, LoginMentorApi
from .user import UserApi, MentorApi, UserImageApi, ImageApi, FollowApi
from .reset_password import ForgotPassword, ResetPassword
from .post import PostsApi, PostApi, CommentApi, LikeApi, RecommendationsApi
from .search import ResultsApi, SuggestionsApi
from .chat import ChatsApi, ChatApi, JoinApi, MessagesApi, LeaveApi, PromoteApi, RemoveApi

def initialize_routes(api):
    api.add_resource(FollowApi, '/api/users/follow/<id>')
    api.add_resource(MoviesApi, '/api/movies')
    api.add_resource(MovieApi, '/api/movies/<id>')
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(SignupMentorApi, '/api/auth/mentor/signup')
    api.add_resource(LoginApi, '/api/auth/login')
    api.add_resource(LoginMentorApi, '/api/auth/mentor/login')
    api.add_resource(UserImageApi, '/api/user/image/<id>')
    api.add_resource(ImageApi, '/api/image/<filename>')
    api.add_resource(UserApi, '/api/user/<id>')
    api.add_resource(MentorApi, '/api/mentor/<id>')
    api.add_resource(ConfirmApi, '/confirm')
    api.add_resource(ForgotPassword, '/api/auth/forgot')
    api.add_resource(ResetPassword, '/api/auth/reset')
    api.add_resource(InterestsApi, '/api/interests')
    api.add_resource(InterestApi, '/api/interests/<id>')
    api.add_resource(CountriesApi, '/api/countries')
    api.add_resource(CountryApi, '/api/countries/<id>')
    api.add_resource(RecommendationsApi, '/api/posts/recommendations')
    api.add_resource(PostsApi, '/api/posts')
    api.add_resource(PostApi, '/api/posts/<id>')
    api.add_resource(CommentApi, '/api/comments/<post_id>')
    api.add_resource(LikeApi, '/api/likes/<post_id>')
    api.add_resource(ResultsApi, '/api/results/<search>')
    api.add_resource(SuggestionsApi, '/api/suggestions/<search>')
    api.add_resource(ChatsApi, '/api/chats')
    api.add_resource(ChatApi, '/api/chats/<id>')
    api.add_resource(JoinApi, '/api/chats/join/<host_id>')
    api.add_resource(LeaveApi, '/api/chats/leave/<id>')
    api.add_resource(PromoteApi, '/api/chats/promote/<id>')
    api.add_resource(MessagesApi, '/api/chats/messages/<id>')
    api.add_resource(RemoveApi, '/api/chats/remove/<id>')
