import os
import json
import operator
import datetime
from app import app
from bson import ObjectId, json_util
from flask_restful import Resource
from flask import Response, request, send_from_directory
from database.models import User, Post, Mentor
from bson.json_util import dumps
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from mongoengine.errors import FieldDoesNotExist, \
NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, \
InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_post(post):
    data = post.to_mongo()

    if post.comments:
        data['comments'] = [convert_ob(ob) for ob in post.comments]
    if post.likes:
        data['likes'] = [convert_ob(ob) for ob in post.likes]
    if post.author:
        data['author'] = User.objects.only('name', 'surname', 'image').get(id=post.author.id).to_mongo()

    return data

def convert_ob(ob):
    author = User.objects.only('name', 'surname', 'image', 'confirmed_at').get(id=ob.author.id).to_mongo()

    ob = ob.to_mongo()
    ob['author'] = author

    return ob

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

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
            return { 'success': True }, 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
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
            raise MovieNotExistsError
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
            return { 'success': True }, 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
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

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                body = {
                    'image': filename
                }
                user.update(**body)
                return { 'success': True, 'image': filename }, 200
            else:
                return { 'error': True, 'payload': 'Something went wrong' }, 400
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
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
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

class ImageApi(Resource):
    def get(self, filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
