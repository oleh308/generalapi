import timestring
from dateutil.parser import parse
from flask_restful import Resource
from flask import Response, request
from utils.convert import JSONEncoder
from mongoengine.queryset.visitor import Q
from database.models import User, Session, Chat
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.convert import convert_session, convert_session_chat

from mongoengine.errors import DoesNotExist, ValidationError
from resources.errors import InternalServerError, SchemaValidationError, DocumentMissing


class SessionsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            chats = Chat.objects(type='private', users__contains=user)

            all_sessions = [convert_session(session) for session in Session.objects(host=user)]
            for chat in chats:
                sessions = Session.objects(chats__contains=chat)
                for session in sessions:
                    all_sessions.append(convert_session_chat(session, chat))

            return Response(JSONEncoder().encode(all_sessions), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            slot_id = body.pop('slot_id')
            host_id = body.pop('host_id')
            chat_id = body.pop('chat_id')
            product_id = body.pop('product_id')

            session = Session(**body, chats=[chat_id], slot=slot_id, host=host_id, product=product_id)
            session.save()

            return {'id': str(session.id)}, 200
        except DoesNotExist:
            raise DocumentMissing
        except ValidationError:
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError


class SessionApi(Resource):
    @jwt_required
    def patch(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()

            user = User.objects.get(id=user_id)
            Session.objects.get(id=id).update(**body)

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

    @jwt_required
    def delete(self, id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            session = Session.objects.get(id=id)
            session.delete()

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except ValidationError:
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError


class SessionJoinApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()

            user = User.objects.get(id=user_id)
            chat = Chat.objects.get(id=body['chat'])
            session = Session.objects.get(id=id)

            if chat in session.chats:
                raise InternalServerError

            session.chats.append(chat)
            session.save()

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError


class SessionLeaveApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()

            user = User.objects.get(id=user_id)
            chat = Chat.objects.get(id=body['chat'])

            session = Session.objects.get(id=id, chats__contains=chat)
            session.chats.remove(chat)
            session.save()

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError
