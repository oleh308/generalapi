import re
import operator
from flask_restful import Resource
from flask import Response, request
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.convert import convert_user, JSONEncoder, convert_post
from database.models import User, Post, Comment, Like, Mentor, Interest

from mongoengine.errors import DoesNotExist
from resources.errors import DocumentMissing, InternalServerError


def filter_users(users, regex):
    results = []
    for user in users:
        if regex.match(user.name):
            results.append(user)
        elif regex.match(user.surname):
            results.append(user)
        elif regex.match(user.name + ' ' + user.surname):
            results.append(user)

    return results

class ResultsApi(Resource):
    @jwt_required
    def get(self, search):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

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
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError


class SuggestionsApi(Resource):
    @jwt_required
    def get(self, search):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

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
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError
