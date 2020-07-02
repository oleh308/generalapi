from flask_restful import Resource
from flask import Response, request
from database.models import User, Interest
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import FieldDoesNotExist, \
NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, \
InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError

class InterestsApi(Resource):
    def get(self):
        interests = Interest.objects().to_json()
        return Response(interests, mimetype="application/json", status=200)

    def post(self):
        try:
            body = request.get_json()
            interest = Interest(**body)
            interest.save()
            id = interest.id
            return {'id': str(id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise MovieAlreadyExistsError
        except Exception as e:
            raise InternalServerError

class InterestApi(Resource):
    def put(self, id):
        try:
            interest = Interest.objects.get(id=id)
            body = request.get_json()
            Interest.objects.get(id=id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

    def delete(self, id):
        try:
            interest = Interest.objects.get(id=id)
            interest.delete()
            return '', 200
        except DoesNotExist:
            raise DeletingMovieError
        except Exception:
            raise InternalServerError

    def get(self, id):
        try:
            interest = Interest.objects.get(id=id).to_json()
            return Response(interest, mimetype="application/json", status=200)
        except DoesNotExist:
            raise MovieNotExistsError
        except Exception:
            raise InternalServerError
