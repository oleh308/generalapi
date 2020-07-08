import timestring
from dateutil.parser import parse
from flask_restful import Resource
from flask import Response, request
from utils.convert import JSONEncoder
from utils.convert import convert_session
from mongoengine.queryset.visitor import Q
from database.models import User, Session, Chat
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import DoesNotExist, ValidationError
from resources.errors import InternalServerError, SchemaValidationError, DocumentMissing


class SessionsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            sessions = Session.objects(Q(user=user) | Q(mentor=user))
            sessions = [convert_session(session) for session in sessions]

            return Response(JSONEncoder().encode(sessions), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            host_id = body.pop('host_id')
            chat_id = body.pop('chat_id')
            other_id = body.pop('user_id')

            if user_id == host_id:
                session = Session(**body, user=other_id, mentor=host_id, chat=chat_id)
                session.save()
            else:
                session = Session(**body, user=user_id, mentor=host_id, chat=chat_id)
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
