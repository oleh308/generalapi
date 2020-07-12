from flask_restful import Resource
from flask import Response, request
from utils.convert import JSONEncoder
from database.models import User, Calendar, Slot
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import FieldDoesNotExist, \
    NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
from resources.errors import SchemaValidationError, InternalServerError, DocumentMissing


def change_day_array(calendar, slot, day_key, to_add):
    if day_key == 'mon':
        if to_add:
            calendar.mon_slots.append(slot)
        else:
            calendar.mon_slots.remove(slot)
    elif day_key == 'tue':
        if to_add:
            calendar.tue_slots.append(slot)
        else:
            calendar.tue_slots.remove(slot)
    elif day_key == 'wed':
        if to_add:
            calendar.wed_slots.append(slot)
        else:
            calendar.wed_slots.remove(slot)
    elif day_key == 'thu':
        if to_add:
            calendar.thu_slots.append(slot)
        else:
            calendar.thu_slots.remove(slot)
    elif day_key == 'fri':
        if to_add:
            calendar.fri_slots.append(slot)
        else:
            calendar.fri_slots.remove(slot)
    elif day_key == 'sat':
        if to_add:
            calendar.sat_slots.append(slot)
        else:
            calendar.sat_slots.remove(slot)
    elif day_key == 'sun':
        if to_add:
            calendar.sun_slots.append(slot)
        else:
            calendar.sun_slots.remove(slot)


class CalendarsApi(Resource):
    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            calendar = Calendar.objects.filter(user=user_id).first()
            if calendar:
                return { 'error': True, 'payload': 'Calendar already exists.' }, 404

            body = request.get_json()
            calendar = Calendar(**body, user=user_id)
            calendar.save()

            return { 'id': str(calendar.id) }, 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError

    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            calendar = Calendar.objects.get(user=user_id).to_mongo()

            return Response(JSONEncoder().encode(calendar), mimetype="application/json", status=200)
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class CalendarSlotsApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            product = body.pop('product')
            day_key = body.pop('day_key')
            calendar = Calendar.objects.get(id=id, user=user_id)

            slot = Slot(**body, product=product)
            slot.save()

            change_day_array(calendar, slot, day_key, True)
            calendar.save()

            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class CalendarSlotApi(Resource):
    @jwt_required
    def delete(self, id, slot_id):
        try:
            slot = Slot.objects.get(id=slot_id, calendar=id)
            slot.delete()

            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError






    #
    # def patch(self):
    #     try:
    #         user_id = get_jwt_identity()
    #         body = request.get_json()
    #
    #         Calendar.objects.get(user=user_id).update(**body)
    #         calendar = Calendar(**body, user=user_id)
    #         calendar.save()
    #
    #         return { 'id': str(calendar.id) }, 200
    #     except InvalidQueryError:
    #         raise SchemaValidationError
    #     except DoesNotExist:
    #         raise DocumentMissing
    #     except Exception:
    #         raise InternalServerError
    #
    #
    # @jwt_required
    # def delete(self, user_id):
    #     try:
    #         owner_id = get_jwt_identity()
    #         if user_id != owner_id:
    #             return { 'error': True, 'payload': 'Not authorized.' }, 404
    #
    #         calendar = calendar.objects.get(user=owner_id)
    #         calendar.delete()
    #
    #         return '', 200
    #     except DoesNotExist:
    #         raise DeletingMovieError
    #     except Exception:
    #         raise InternalServerError
    #
    # @jwt_required
    # def get(self, user_id):
    #     try:
    #         calendar = Calendar.objects.get(user=user_id).to_mongo()
    #
    #         return Response(JSONEncoder().encode(calendar), mimetype="application/json", status=200)
    #     except DoesNotExist:
    #         raise DocumentMissing
    #     except Exception:
    #         raise InternalServerError
