from flask_restful import Resource
from flask import Response, request
from database.models import User, Country
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import FieldDoesNotExist, \
NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, \
InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError

class CountriesApi(Resource):
    def get(self):
        countries = Country.objects().to_json()
        return Response(countries, mimetype="application/json", status=200)

    def post(self):
        try:
            body = request.get_json()
            print(body)
            country = Country(**body)
            country.save()
            id = country.id
            return {'id': str(id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise MovieAlreadyExistsError
        except Exception as e:
            raise InternalServerError

class CountryApi(Resource):
    def put(self, id):
        try:
            country = Country.objects.get(id=id)
            body = request.get_json()
            Country.objects.get(id=id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

    def delete(self, id):
        try:
            country = Country.objects.get(id=id)
            country.delete()
            return '', 200
        except DoesNotExist:
            raise DeletingMovieError
        except Exception:
            raise InternalServerError

    def get(self, id):
        try:
            country = Country.objects.get(id=id).to_json()
            return Response(country, mimetype="application/json", status=200)
        except DoesNotExist:
            raise MovieNotExistsError
        except Exception:
            raise InternalServerError
