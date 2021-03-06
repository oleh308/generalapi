import json
import datetime
from bson import json_util, ObjectId

from database.models import User, Message, ChatInfo, Mentor

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def get_last_message(chat):
    messages = chat.messages.copy()
    messages.reverse()

    for message in messages:
        if message.type == 'basic':
            return message

    return None

def get_last_seen_message(chat, user):
    chat_info = ChatInfo.objects(chat=chat, user=user).first()
    if chat_info:
        return chat_info.message
    else:
        return None

def convert_chat_basic(chat, user):
    host = chat.host
    last_message = get_last_message(chat)
    last_seen_message = get_last_seen_message(chat, user)

    chat = chat.to_mongo()
    chat['host'] = get_user_basic(host)

    if last_message:
        chat['last_message'] = last_message.to_mongo()

    if last_seen_message:
        chat['last_seen_message'] = last_seen_message.to_mongo()

    return chat

def convert_with_author(ob):
    author = ob.author

    ob = ob.to_mongo()
    ob['author'] = get_user_basic(author)

    return ob

def convert_chat_full(chat):
    data = chat.to_mongo()
    data['host'] = get_user_basic(chat.host)
    data['users'] = [get_user_basic(user) for user in chat.users]
    data['admins'] = [get_user_basic(user) for user in chat.admins]
    data['topics'] = [topic.to_mongo() for topic in chat.topics]
    data['messages'] = [convert_with_author(message) for message in chat.messages]

    return data

def convert_ob(ob):
    author = get_user_basic(User.objects.get(id=ob.author.id))

    ob = ob.to_mongo()
    ob['author'] = author

    return ob

def convert_session(session):
    data = session.to_mongo()

    data['slot'] = session.slot.to_mongo()
    data['host'] = get_user_basic(session.host)

    return data

def convert_session_chat(session, chat):
    data = session.to_mongo()

    data['slot'] = session.slot.to_mongo()
    data['host'] = get_user_basic(session.host)
    data['chat'] = str(chat.id)

    return data

def convert_post(post):
    data = post.to_mongo()

    if post.comments:
        data['comments'] = [convert_ob(ob) for ob in post.comments]
    if post.likes:
        data['likes'] = [convert_ob(ob) for ob in post.likes]
    if post.author:
        data['author'] = get_user_basic(User.objects.get(id=post.author.id))

    data['created_at'] = data['created_at'].isoformat()

    return data

def convert_product(product):
    data = product.to_mongo()

    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
    for day in days:
        key = day + '_slots'
        data[key] = [slot.to_mongo() for slot in product[key]]

    return data

def get_user_basic(user):
    data = {
        '_id': user.id,
        'name': user.name,
        'image': user.image,
        'surname': user.surname
    }

    return data

def convert_user(user):
    mentor = Mentor.objects.get(id=user.mentor.id).to_mongo()

    user = user.to_mongo()
    user['mentor'] = mentor

    return user
