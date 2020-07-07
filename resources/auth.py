import datetime
from app import app
from flask_restful import Resource
from database.models import User, Mentor
from services.mail_service import send_email
from flask import Response, request, render_template
from flask_jwt_extended import create_access_token, decode_token
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError
from resources.errors import SchemaValidationError, EmailAlreadyExistsError, UnauthorizedError, InternalServerError

class SignupApi(Resource):
    def post(self):
        url = request.host_url + 'confirm?confirm_token='

        try:
            body = request.get_json()
            user = User(**body)
            user.confirmed = False
            user.hash_password()

            user.save()
            id = user.id

            expires = datetime.timedelta(hours=24)
            confirm_token = create_access_token(str(user.id), expires_delta=expires)
            send_email('[GeneralAPI] Confirm your email',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[user.email],
                              text_body=render_template('email/confirmation.txt',
                                                        url=url + confirm_token),
                              html_body=render_template('email/confirmation.html',
                                                        url=url + confirm_token))

            return { 'id': str(id) }, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except ConnectionRefusedError:
            raise InternalServerError('[MAIL] connection refused')
        except Exception as e:
            raise InternalServerError

class SignupMentorApi(Resource):
    def post(self):
        url = request.host_url + 'confirm?confirm_token='

        try:
            body = request.get_json()
            mentor_default = { 'status': 'pending' }
            mentor = Mentor(**mentor_default)
            mentor.save()
            user = User(**body, mentor=mentor)
            user.confirmed = False
            user.hash_password()
            user.save()
            id = user.id

            expires = datetime.timedelta(hours=24)
            confirm_token = create_access_token(str(user.id), expires_delta=expires)
            send_email('[GeneralAPI] Confirm your email',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[user.email],
                              text_body=render_template('email/confirmation.txt',
                                                        url=url + confirm_token),
                              html_body=render_template('email/confirmation.html',
                                                        url=url + confirm_token))

            return { 'id': str(id) }, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except ConnectionRefusedError:
            raise InternalServerError('[MAIL] connection refused')
        except Exception as e:
            raise InternalServerError


class ConfirmApi(Resource):
    def get(self):
        try:
            reset_token = request.args.get('confirm_token')

            if not reset_token:
                raise SchemaValidationError

            user_id = decode_token(reset_token)['identity']

            user = User.objects.get(id=user_id)
            user.modify(confirmed=True)
            user.modify(confirmed_at=datetime.datetime.now())
            user.save()

            return { 'success': True }, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            raise InternalServerError


class LoginApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(email=body.get('email'))
            authorized = user.check_password(body.get('password'))
            if not authorized:
                return {'error': 'Email or password invalid', 'type': 'notValid'}, 401

            if not user.confirmed:
                return {'error': 'Email is not confirmed', 'type': 'confirmationRequired'}, 401

            if user.mentor:
                if user.mentor.status == 'pending':
                    return {'error': "Mentor's status is spending", 'type': 'mentorIsPending'}, 401

                if user.mentor.status == 'cancelled':
                    return {'error': 'Mentor was not approved', 'type': 'mentorIsNotApproved'}, 401


            prev_login = user.first_login
            if user.first_login:
                user.modify(first_login=False)
                user.save()

            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)

            return_ob = {
                'token': access_token,
                'user_id': str(user.id),
                'first_login': prev_login,
                'is_mentor': False
            }

            if user.mentor:
                return_ob['is_mentor'] = True

            return return_ob, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            raise InternalServerError
