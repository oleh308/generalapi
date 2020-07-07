from flask_restful import Resource
from flask import Response, request
from utils.convert import JSONEncoder
from database.models import User, Product
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import DoesNotExist, ValidationError
from resources.errors import InternalServerError, SchemaValidationError, DocumentMissing


class ProductsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            products = Product.objects(user=user)
            products = [product.to_mongo() for product in products]

            return Response(JSONEncoder().encode(products), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()

            user = User.objects.get(id=user_id)
            product = Product(**body, user=user)
            user.products.append(product)

            product.save()
            user.save()

            return {'id': str(product.id)}, 200
        except DoesNotExist:
            raise DocumentMissing
        except ValidationError:
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError


class ProductApi(Resource):
    @jwt_required
    def patch(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()

            user = User.objects.get(id=user_id)
            Product.objects.get(id=id, user=user).update(**body)

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

            product = Product.objects.get(id=id, user=user)
            product.delete()

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except ValidationError:
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError
