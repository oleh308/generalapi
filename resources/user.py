import operator
from app import app
from utils.file import save_file
from flask_restful import Resource
from flask import Response, request
from utils.convert import JSONEncoder, convert_post
from database.models import User, Post, Mentor, Product
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import DoesNotExist, ValidationError, InvalidQueryError
from resources.errors import SchemaValidationError, \
    InternalServerError, DocumentMissing

class UserApi(Resource):
    @jwt_required
    def put(self, id):
        try:
            user_id = get_jwt_identity()
            if user_id != id:
                return { 'error': True, 'payload': 'Not authorised' }, 401

            user = User.objects.get(id=id)
            body = request.get_json()
            User.objects.get(id=id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError

    @jwt_required
    def get(self, id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.exclude('password').get(id=id)
            data = user.to_mongo()

            if user.mentor:
                data['mentor'] = user.mentor.to_mongo()
                data['posts'] = [convert_post(ob) for ob in Post.objects.filter(author=id)]
                data['posts'].sort(key=operator.itemgetter('created_at'), reverse=True)

            return Response(JSONEncoder().encode(data), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class MentorApi(Resource):
    @jwt_required
    def put(self, id):
        try:
            user_id = get_jwt_identity()
            if user_id != id:
                return { 'error': True, 'payload': 'Not authorised' }, 401

            user = User.objects.get(id=id)
            body = request.get_json()
            user.mentor.update(**body)

            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class UserProductsApi(Resource):
    @jwt_required
    def get(self, user_id):
        try:
            products = Product.objects(user=user_id)
            products = [product.to_mongo() for product in products]

            return Response(JSONEncoder().encode(products), mimetype="application/json", status=200)
        except Exception:
            raise InternalServerError


class UserImageApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()

            if user_id != id:
                return { 'error': True, 'payload': 'Not authorised' }, 401

            if 'file' not in request.files:
                return { 'error': True, 'payload': 'File not found' }, 404

            file = request.files['file']
            user = User.objects.get(id=id)

            if request.files and 'file' in request.files:
                file = request.files['file']
                filename = str(user.id) + file.filename

                if save_file(filename, file):
                    user.update(image=filename)

                return { 'image': filename }, 200
            else:
                return { 'error': True, 'payload': 'Something went wrong' }, 400
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class FollowApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            to_follow = User.objects.get(id=id)

            if not to_follow or not user:
                return { 'error': True, 'payload': 'User not found' }, 404

            if to_follow in user.following:
                to_follow.followers.remove(user)
                user.following.remove(to_follow)
            else:
                to_follow.followers.append(user)
                user.following.append(to_follow)

            to_follow.save()
            user.save()
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError
