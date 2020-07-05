import os
import json
import operator
import datetime
from app import app
from bson import json_util, ObjectId
from flask_restful import Resource
from flask import Response, request
from database.models import User, Post, Comment, Like
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app import socketio

from mongoengine.errors import FieldDoesNotExist, \
NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, \
InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_post(post):
    author = post.author.to_mongo()
    likes = [convert_ob(ob) for ob in post.likes]
    post = post.to_mongo()
    author = {
        'name': author['name'],
        'id': str(author['_id']),
        'surname': author['surname'],
        'image': author['image']
    }
    post['_id'] = str(post['_id'])
    post['author'] = author
    post['likes'] = likes
    post['created_at'] = post['created_at'].isoformat()

    return post

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

class PostsApi(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        if not user:
            return { 'error': True, 'payload': 'User not found' }, 404

        ids = user.following
        ids.append(user)

        posts = Post.objects(author__in=ids)
        posts = [convert_post(ob) for ob in posts]
        posts.sort(key=operator.itemgetter('created_at'), reverse=True)
        return Response(JSONEncoder().encode(posts), mimetype="application/json", status=200)

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            body = {
                'title': request.form['title'],
                'content': request.form['content'],
                'hashtags': request.form.getlist('hashtags[]')
            }
            post = Post(**body, author=user)
            post.save()

            if request.files and 'file' in request.files:
                file = request.files['file']

                filename = 'image' + str(post.id) + '.' + file.filename.rsplit('.', 1)[1].lower()
                if allowed_file(filename):
                    filename = secure_filename(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    post.update(set__image=filename)

            socketio.emit('update', {}, room='mentor' + str(user.id))

            return {'id': str(post.id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise MovieAlreadyExistsError
        except Exception as e:
            raise InternalServerError

class PostApi(Resource):
    @jwt_required
    def put(self, id):
        try:
            post = Post.objects.get(id=id)
            if not post:
                return { 'error': True, 'payload': 'Post not found' }, 404

            body = {
                'title': request.form['title'],
                'content': request.form['content'],
                'hashtags': request.form.getlist('hashtags[]')
            }

            if request.files and 'file' in request.files:
                file = request.files['file']

                filename = 'image' + str(post.id) + '.' + file.filename.rsplit('.', 1)[1].lower()
                if allowed_file(filename):
                    filename = secure_filename(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    body['image'] = filename

            post.update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

    @jwt_required
    def delete(self, id):
        try:
            post = Post.objects.get(id=id)
            post.delete()
            return '', 200
        except DoesNotExist:
            raise DeletingMovieError
        except Exception:
            raise InternalServerError

    @jwt_required
    def get(self, id):
        try:
            post = Post.objects.get(id=id)
            comments = Comment.objects(post=post)
            data = post.to_mongo()
            if post.comments:
                data['comments'] = [convert_ob(ob) for ob in post.comments]
            if post.likes:
                data['likes'] = [convert_ob(ob) for ob in post.likes]
            if post.author:
                data['author'] = User.objects.only('name', 'surname', 'image').get(id=post.author.id).to_mongo()
            return Response(JSONEncoder().encode(data), mimetype="application/json", status=200)
        except DoesNotExist:
            raise MovieNotExistsError
        except Exception:
            raise InternalServerError

class LikeApi(Resource):
    @jwt_required
    def post(self, post_id):
        try:
            user_id = get_jwt_identity()
            post = Post.objects.get(id=post_id)
            user = User.objects.get(id=user_id)
            if not user or not post:
                return { 'error': True, 'payload': 'User not found' }, 404

            like = None
            if Like and Like.objects:
                like = Like.objects.filter(post=post_id, author=user).first()

            if like:
                like.delete()
                socketio.emit('update', {}, room='post' + str(post.id))

                return '', 200
            else:
                body = request.get_json()
                like = Like(**body, post=post, author=user)
                like.save()

                post.likes.append(like)
                post.save()

                id = like.id
                socketio.emit('update', {}, room='post' + str(post.id))

                return {'id': str(id)}, 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

class RecommendationsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            if not user:
                return { 'error': True, 'payload': 'User not found' }, 404

            ids = user.following
            ids.append(user)

            posts = Post.objects.filter(author__nin=ids, hashtags__in=user.interests)

            if len(posts) == 0:
                posts = Post.objects.filter(author__nin=ids)

            posts = [convert_post(ob) for ob in posts]
            posts.sort(key=operator.itemgetter('created_at'), reverse=True)
            return Response(JSONEncoder().encode(posts), mimetype="application/json", status=200)
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

class CommentApi(Resource):
    @jwt_required
    def post(self, post_id):
        try:
            user_id = get_jwt_identity()
            post = Post.objects.get(id=post_id)
            user = User.objects.get(id=user_id)
            if not user or not post:
                return { 'error': True, 'payload': 'User or post not found' }, 404

            print(post, user.posts)
            body = request.get_json()
            comment = Comment(**body, post=post, author=user)
            comment.save()

            post.comments.append(comment)
            post.save()

            id = comment.id
            socketio.emit('update', {}, room='post' + str(post.id))

            return {'id': str(id)}, 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingMovieError
        except Exception:
            raise InternalServerError

    # @jwt_required
    # def delete(self, id):
    #     try:
    #         post = Post.objects.get(id=id)
    #         post.delete()
    #         return '', 200
    #     except DoesNotExist:
    #         raise DeletingMovieError
    #     except Exception:
    #         raise InternalServerError
    #
    # @jwt_required
    # def get(self, id):
    #     try:
    #         post = Post.objects.get(id=id)
    #         data = post.to_mongo()
    #         if post.comments:
    #             data['comments'] = [convert_comment(ob) for ob in post.comments]
    #         if post.author:
    #             data['author'] = User.objects.only('name', 'surname', 'image').get(id=post.author.id).to_mongo()
    #         return Response(JSONEncoder().encode(data), mimetype="application/json", status=200)
    #     except DoesNotExist:
    #         raise MovieNotExistsError
    #     except Exception:
    #         raise InternalServerError
