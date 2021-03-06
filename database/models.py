from .db import db
import datetime
from flask_bcrypt import generate_password_hash, check_password_hash

class Movie(db.Document):
    name = db.StringField(required=True, unique=True)
    casts = db.ListField(db.StringField(), required=True)
    genres = db.ListField(db.StringField(), required=True)
    added_by = db.ReferenceField('User')

class Product(db.Document):
    cost = db.DecimalField(default=1)
    amount = db.DecimalField(default=1)
    content = db.StringField(default='')
    capacity = db.DecimalField(default=1)
    title = db.StringField(required=True, default='')
    mon_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    tue_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    wed_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    thu_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    fri_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    sat_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    sun_slots = db.ListField(db.ReferenceField('Slot'), default=[])
    disabled = db.ListField(db.ReferenceField('DateSlot'), default=[])
    user = db.ReferenceField('User')

class Slot(db.Document):
    duration = db.DecimalField(required=True)
    end_time = db.StringField(required=True)
    capacity = db.DecimalField(required=True)
    start_time = db.StringField(required=True)
    product = db.ReferenceField('Product')

class DateSlot(db.Document):
    date = db.StringField(required=True)
    end_time = db.StringField(required=True)
    start_time = db.StringField(required=True)
    product = db.ReferenceField('Product', required=True)

class Calendar(db.Document):
    mon_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    tue_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    wed_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    thu_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    fri_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    sat_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    sun_slots = db.ListField(db.ReferenceField('Slot'), default=[], reverse_delete_rule=db.PULL)
    disabled = db.ListField(db.ReferenceField('DateSlot'), default=[])
    user = db.ReferenceField('User')

class Session(db.Document):
    comment = db.StringField(default='')
    status = db.StringField(required=True)
    end_date = db.StringField(required=True)
    start_date = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    slot = db.ReferenceField('Slot', required=True)
    host = db.ReferenceField('User', required=True)
    product = db.ReferenceField('User', required=True)
    chats = db.ListField(db.ReferenceField('Chat'), default=[])

class Topic(db.Document):
    content = db.StringField(default='')
    title = db.StringField(required=True, default='')
    chat = db.ReferenceField('Chat')
    end = db.ReferenceField('Message')
    start = db.ReferenceField('Message', required=True)

class ToDoAction(db.Document):
    title = db.StringField(default='')
    completed = db.BooleanField(default=False)
    author = db.ReferenceField('User', required=True)

class Message(db.Document):
    type = db.StringField(default='basic')
    text = db.StringField(required=True, default='')
    images = db.ListField(db.StringField(), default=[])
    created_at = db.DateTimeField(default=datetime.datetime.now)
    chat = db.ReferenceField('Chat')
    author = db.ReferenceField('User')

class ChatInfo(db.Document):
    chat = db.ReferenceField('Chat')
    user = db.ReferenceField('User')
    message = db.ReferenceField('Message')

class Chat(db.Document):
    host = db.ReferenceField('User')
    image = db.StringField(default='')
    capacity = db.DecimalField(default=-1)
    type = db.StringField(default='public')
    product = db.ReferenceField('Product', default=None)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    users = db.ListField(db.ReferenceField('User'), default=[])
    admins = db.ListField(db.ReferenceField('User'), default=[])
    actions = db.ListField(db.ReferenceField('ToDoAction'), default=[])
    topics = db.ListField(db.ReferenceField('Topic', reverse_delete_rule=db.PULL), default=[])
    messages = db.ListField(db.ReferenceField('Message', reverse_delete_rule=db.PULL), default=[])

class Comment(db.Document):
    text = db.StringField(required=True)
    likes = db.DecimalField(required=True, default=0)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    post = db.ReferenceField('Post')
    author = db.ReferenceField('User')

class Like(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now)
    author = db.ReferenceField('User')
    post = db.ReferenceField('Post')

class Interest(db.Document):
    title = db.StringField(required=True, unique=True)

class Country(db.Document):
    code = db.StringField(required=True, unique=True)
    title = db.StringField(required=True, unique=True)

class Post(db.Document):
    title = db.StringField()
    content = db.StringField(required=True)
    image = db.StringField(default='')
    hashtags = db.ListField(db.StringField())
    author =  db.ReferenceField('User')
    likes = db.ListField(db.ReferenceField('Like', reverse_delete_rule=db.PULL))
    created_at = db.DateTimeField(default=datetime.datetime.now)
    comments = db.ListField(db.ReferenceField('Comment', reverse_delete_rule=db.PULL))

class Mentor(db.Document):
    status = db.StringField(required=True)
    areas = db.ListField(db.StringField())

class User(db.Document):
    about = db.StringField()
    confirmed_at = db.DateTimeField()
    image = db.StringField(default='')
    name = db.StringField(required=True)
    city = db.StringField(required=False)
    surname = db.StringField(required=True)
    country = db.StringField(required=False)
    interests = db.ListField(db.StringField())
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)
    confirmed = db.BooleanField(required=False, default=False)
    first_login = db.BooleanField(required=False, default=True)
    mentor = db.ReferenceField('Mentor', reverse_delete_rule=db.CASCADE)
    following = db.ListField(db.ReferenceField('User'), default=[])
    followers = db.ListField(db.ReferenceField('User'), default=[])
    products = db.ListField(db.ReferenceField('Product', reverse_delete_rule=db.PULL))
    posts = db.ListField(db.ReferenceField('Post', reverse_delete_rule=db.PULL))
    recent_searches = db.ListField(db.StringField(), default=[])
#    movies = db.ListField(db.ReferenceField('Movie', reverse_delete_rule=db.PULL))

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

User.register_delete_rule(Post, 'author', db.CASCADE)
User.register_delete_rule(Comment, 'author', db.CASCADE)
User.register_delete_rule(Product, 'user', db.CASCADE)
Post.register_delete_rule(Comment, 'post', db.CASCADE)
Post.register_delete_rule(Like, 'post', db.CASCADE)
Chat.register_delete_rule(Message, 'chat', db.CASCADE)
Chat.register_delete_rule(Topic, 'chat', db.CASCADE)

# User.register_delete_rule(Movie, 'added_by', db.CASCADE)
