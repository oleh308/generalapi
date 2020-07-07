import operator
from app import app, socketio
from utils.file import save_file
from flask_restful import Resource
from flask import Response, request
from utils.convert import JSONEncoder, convert_post
from database.models import User, Post, Comment, Like
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import FieldDoesNotExist, \
    DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, InternalServerError

class PostsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            ids = user.following
            ids.append(user)

            posts = Post.objects(author__in=ids)
            posts = [convert_post(ob) for ob in posts]
            posts.sort(key=operator.itemgetter('created_at'), reverse=True)

            return Response(JSONEncoder().encode(posts), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

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
                filename = str(post.id) + file.filename

                if save_file(filename, file):
                    post.update(set__image=filename)

            socketio.emit('update', {}, room='mentor' + str(user.id))

            return {'id': str(post.id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

class PostApi(Resource):
    @jwt_required
    def put(self, id):
        try:
            post = Post.objects.get(id=id)
            body = {
                'title': request.form['title'],
                'content': request.form['content'],
                'hashtags': request.form.getlist('hashtags[]')
            }

            if request.files and 'file' in request.files:
                file = request.files['file']
                filename = str(post.id) + file.filename

                if save_file(filename, file):
                    body['image'] = filename

            post.update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError

    @jwt_required
    def delete(self, id):
        try:
            post = Post.objects.get(id=id)
            post.delete()
            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError

    @jwt_required
    def get(self, id):
        try:
            post = Post.objects.get(id=id)
            return Response(convert_post(post), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class LikeApi(Resource):
    @jwt_required
    def post(self, post_id):
        try:
            user_id = get_jwt_identity()
            post = Post.objects.get(id=post_id)
            user = User.objects.get(id=user_id)

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
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class RecommendationsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

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
            raise DocumentMissing
        except Exception:
            raise InternalServerError

class CommentApi(Resource):
    @jwt_required
    def post(self, post_id):
        try:
            user_id = get_jwt_identity()
            post = Post.objects.get(id=post_id)
            user = User.objects.get(id=user_id)

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
            raise DocumentMissing
        except Exception:
            raise InternalServerError

    @jwt_required
    def delete(self, id):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            comment = Comment.objects.get(id=id, author=user)
            comment.delete()

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError
