from .auth_routes import auth_routes
from .users_routes import users_routes
from .posts_routes import posts_routes
from .chats_routes import chats_routes
from .files_routes import files_routes
from .search_routes import search_routes
from .password_routes import password_routes
from .sessions_routes import sessions_routes
from .products_routes import products_routes
from .calendar_routes import calendar_routes

from .countries_routes import countries_routes
from .interests_routes import interests_routes
def initialize_routes(api):
    auth_routes(api)
    users_routes(api)
    posts_routes(api)
    chats_routes(api)
    files_routes(api)
    search_routes(api)
    password_routes(api)
    products_routes(api)
    sessions_routes(api)
    calendar_routes(api)
    countries_routes(api)
    interests_routes(api)
