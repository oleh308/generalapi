import os
import re
import json
import operator
import datetime
from app import app
from flask_restful import Resource
from flask import Response, request
from bson import json_util, ObjectId
from mongoengine.queryset.visitor import Q
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
from database.models import User, Post, Comment, Like, Mentor, Interest
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import FieldDoesNotExist, \
NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from resources.errors import SchemaValidationError, MovieAlreadyExistsError, \
InternalServerError, UpdatingMovieError, DeletingMovieError, MovieNotExistsError


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
    author = User.objects.get(id=ob.author.id).to_mongo()

    ob = ob.to_mongo()
    ob['author'] = author

    return ob

def convert_user(user):
    mentor = Mentor.objects.get(id=user.mentor.id).to_mongo()

    user = user.to_mongo()
    user['mentor'] = mentor

    return user

def filter_users(users, regex):
    results = []
    print(users)
    for user in users:
        if regex.match(user.name):
            results.append(user)
        elif regex.match(user.surname):
            results.append(user)
        elif regex.match(user.name + ' ' + user.surname):
            results.append(user)

    return results

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

class ResultsApi(Resource):
    @jwt_required
    def get(self, search):
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        if not user:
            return { 'error': True, 'payload': 'User not found' }, 404

        regex = re.compile('.*' + search + '.*', re.IGNORECASE)

        posts = Post.objects.filter(Q(title=regex) | Q(content=regex) | Q(hashtags__icontains=search))
        posts = [convert_post(ob) for ob in posts]
        posts.sort(key=operator.itemgetter('created_at'), reverse=True)

        users = filter_users(User.objects(id__ne=user.id), regex)
        users = [convert_user(ob) for ob in users]

        result = {
            'users': users,
            'posts': posts,
            'following': [ob.id for ob in user.following]
        }

        if search not in user.recent_searches:
            print(user.recent_searches, search)
            if len(user.recent_searches) > 4:
                user.recent_searches.pop(0)
            user.recent_searches.append(search)
            user.save()

        return Response(JSONEncoder().encode(result), mimetype="application/json", status=200)

class SuggestionsApi(Resource):
    @jwt_required
    def get(self, search):
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        if not user:
            return { 'error': True, 'payload': 'User not found' }, 404

        regex = re.compile('.*' + search + '.*', re.IGNORECASE)

        posts = Post.objects.filter(title=regex)
        interests = Interest.objects.filter(title=regex)
        users = User.objects.filter(Q(name=regex) | Q(surname=regex))

        posts = [ob.title for ob in posts]
        interests = [ob.title for ob in interests]
        users = [ob.name + ' ' + ob.surname for ob in users]

        suggestions = interests + posts + users

        if len(suggestions) > 5:
            suggestions = suggestions[0:5]
        return Response(JSONEncoder().encode(suggestions), mimetype="application/json", status=200)
