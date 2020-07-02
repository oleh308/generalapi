import json
import datetime
from bson import json_util, ObjectId

from database.models import User, Message

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def convert_chat_basic(chat):
    host = chat.host

    chat = chat.to_mongo()
    chat['host'] = get_user_basic(host)

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

def get_user_basic(user):
    data = {
        '_id': user.id,
        'name': user.name,
        'image': user.image,
        'surname': user.surname
    }

    return data
