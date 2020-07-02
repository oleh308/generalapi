import os
from flask_restful import Resource
from flask import Response, request
from database.models import User, Chat, Message
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import FieldDoesNotExist, \
NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, \
InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError, DocumentMissing

from utils.file import save_file
from werkzeug.utils import secure_filename
from utils.convert import convert_chat_basic, convert_chat_full, JSONEncoder

class ChatsApi(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        if not user:
            return { 'error': True, 'payload': 'User not found' }, 404
        chats = Chat.objects.filter(Q(host=user) | Q(users__contains=user.id) | Q(admins__contains=user.id))

        chats = [convert_chat_basic(chat) for chat in chats]

        return Response(JSONEncoder().encode(chats), mimetype="application/json", status=200)


class ChatApi(Resource):
    @jwt_required
    def get(self, id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            if not user:
                return { 'error': True, 'payload': 'User not found' }, 404
            chat = Chat.objects.filter((Q(host=user) | Q(users__contains=user.id) | Q(admins__contains=user.id)) & Q(id=id)).first()
            if not chat:
                return { 'error': True, 'payload': 'Chat not found' }, 404

            chat = convert_chat_full(chat)

            return Response(JSONEncoder().encode(chat), mimetype="application/json", status=200)

        except Exception as e:
            raise InternalServerError


class JoinApi(Resource):
    @jwt_required
    def post(self, host_id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            host = User.objects.get(id=host_id)

            if not user or not host:
                return { 'error': True, 'payload': 'User not found' }, 404

            chat = Chat.objects(host=host, type='public').first()
            if chat:
                if user not in chat.users and user not in chat.admins and user != chat.host:
                    chat.users.append(user)
            else:
                chat = Chat(host=host)
                chat.users.append(user)

            chat.save()

            return { 'id': str(chat.id) }, 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

class LeaveApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            chat = Chat.objects.get(id=id)

            if user in chat.users:
                chat.users.remove(user)
                message = Message(type='userLeft', text='', author=user)
                chat.messages.append(message)

                message.save()
                chat.save()

                return '', 200
            elif user in chat.admins:
                chat.admins.remove(user)
                message = Message(type='userLeft', text='', author=user)
                chat.messages.append(message)

                message.save()
                chat.save()

                return '', 200

            return '', 404
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

class RemoveApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            body = request.get_json()
            user_id = get_jwt_identity()

            user = User.objects.get(id=user_id)
            to_remove = User.objects.get(id=body['id'])
            chat = Chat.objects.get(id=id)

            if to_remove not in chat.users:
                return '', 401

            to_remove_name = to_remove.name + ' ' + to_remove.surname
            if user in chat.admins or user == chat.host:
                chat.users.remove(to_remove)
                message = Message(type='userRemoved', text='', author=user)
                chat.messages.append(message)

                message.save()
                chat.save()

                return '', 200

            return '', 401
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError


class PromoteApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            body = request.get_json()
            user_id = get_jwt_identity()

            user = User.objects.get(id=user_id)
            to_promote = User.objects.get(id=body['id'])
            chat = Chat.objects.get(host=user, id=id)

            to_promote_name = to_promote.name + ' ' + to_promote.surname
            if to_promote in chat.admins:
                chat.users.append(to_promote)
                chat.admins.remove(to_promote)
                message = Message(type='userDemote', text=to_promote_name, author=user)
                chat.messages.append(message)

                message.save()
                chat.save()

                return '', 200
            elif to_promote in chat.users:
                chat.users.remove(to_promote)
                chat.admins.append(to_promote)
                message = Message(type='userPromote', text=to_promote_name, author=user)
                chat.messages.append(message)

                message.save()
                chat.save()

                return '', 200

            return '', 401
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError


class MessagesApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            chat = Chat.objects.get(id=id)
            user = User.objects.get(id=user_id)

            message = Message(text=request.form['text'], author=user)
            chat.messages.append(message)

            message.save()
            chat.save()

            if 'file[]' in request.files:
                print('here')
                filenames = []
                files = request.files.getlist('file[]')
                for file in files:
                    filename = str(message.id) + file.filename
                    if save_file(filename, file):
                        filenames.append(filename)

                message.images = filenames
                message.save()

            return { 'id': str(message.id) }, 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError
