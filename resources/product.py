from flask_restful import Resource
from flask import Response, request
from database.models import User, Product, Slot, Session
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.convert import JSONEncoder, convert_product, convert_session

from mongoengine.errors import DoesNotExist, ValidationError
from resources.errors import InternalServerError, SchemaValidationError, DocumentMissing

days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

def change_day_array(product, slot, day_key, to_add):
    if day_key == 'mon':
        if to_add:
            product.mon_slots.append(slot)
        else:
            product.mon_slots.remove(slot)
    elif day_key == 'tue':
        if to_add:
            product.tue_slots.append(slot)
        else:
            product.tue_slots.remove(slot)
    elif day_key == 'wed':
        if to_add:
            product.wed_slots.append(slot)
        else:
            product.wed_slots.remove(slot)
    elif day_key == 'thu':
        if to_add:
            product.thu_slots.append(slot)
        else:
            product.thu_slots.remove(slot)
    elif day_key == 'fri':
        if to_add:
            product.fri_slots.append(slot)
        else:
            product.fri_slots.remove(slot)
    elif day_key == 'sat':
        if to_add:
            product.sat_slots.append(slot)
        else:
            product.sat_slots.remove(slot)
    elif day_key == 'sun':
        if to_add:
            product.sun_slots.append(slot)
        else:
            product.sun_slots.remove(slot)

def save_slot(slotData, product):
    slot = Slot(**slotData, product=product)
    slot.save()
    return slot

def remove_slots(product):
    for slot in product.mon_slots:
        slot.delete()
    for slot in product.tue_slots:
        slot.delete()
    for slot in product.wed_slots:
        slot.delete()
    for slot in product.thu_slots:
        slot.delete()
    for slot in product.fri_slots:
        slot.delete()
    for slot in product.sat_slots:
        slot.delete()
    for slot in product.sun_slots:
        slot.delete()


class ProductsApi(Resource):
    @jwt_required
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            products = Product.objects(user=user)
            products = [convert_product(product) for product in products]

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
            product.save()

            for day in days:
                key = day + '_slots'
                product[key] = [save_slot(slot, product) for slot in body[key]]

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
    def get(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()

            product = Product.objects.get(id=id)

            return Response(JSONEncoder().encode(convert_product(product)), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception as e:
            raise InternalServerError

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
            for day in days:
                key = day + '_slots'
                for slot in product[key]:
                    slot.delete()
            product.delete()

            return '', 200
        except DoesNotExist:
            raise DocumentMissing
        except ValidationError:
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError


class ProductSlotsApi(Resource):
    @jwt_required
    def post(self, id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            day_key = body.pop('day_key')
            product = Product.objects.get(id=id, user=user_id)

            slot = Slot(**body, product=product)
            slot.save()

            change_day_array(product, slot, day_key, True)
            product.save()

            return { 'id': str(slot.id) }, 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class ProductSlotApi(Resource):
    @jwt_required
    def delete(self, id, slot_id):
        try:
            user_id = get_jwt_identity()
            product = Product.objects.get(id=id, user=user_id)
            slot = Slot.objects.get(id=slot_id, product=product)

            if slot in product.mon_slots:
                product.mon_slots.remove(slot)
            elif slot in product.tue_slots:
                product.tue_slots.remove(slot)
            elif slot in product.wed_slots:
                product.wed_slots.remove(slot)
            elif slot in product.thu_slots:
                product.thu_slots.remove(slot)
            elif slot in product.fri_slots:
                product.fri_slots.remove(slot)
            elif slot in product.sat_slots:
                product.sat_slots.remove(slot)
            elif slot in product.sun_slots:
                product.sun_slots.remove(slot)

            product.save()
            slot.delete()

            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError

    @jwt_required
    def patch(self, id, slot_id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            product = Product.objects.get(id=id, user=user_id)

            Slot.objects.get(id=slot_id, product=product).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError


class ProductSessionsApi(Resource):
    @jwt_required
    def get(self, id):
        try:
            user_id = get_jwt_identity()
            sessions = Session.objects(product=id)
            sessions = [convert_session(session) for session in sessions]

            return Response(JSONEncoder().encode(sessions), mimetype="application/json", status=200)
        except DoesNotExist:
            raise DocumentMissing
        except Exception:
            raise InternalServerError

#
#
# class ProductSlotApi(Resource):
#     @jwt_required
#     def delete(self, id, slot_id, day_key):
#         try:
#             user_id = get_jwt_identity()
#             body = request.get_json()
#             product = Product.objects.get(id=id, user=user_id)
#
#             slot = Slot.object.get(id=slot_id, product=product)
#
#             change_day_array(product, slot, day_key, False)
#             product.save()
#             slot.delete()
#
#             return '', 200
#         except InvalidQueryError:
#             raise SchemaValidationError
#         except DoesNotExist:
#             raise DocumentMissing
#         except Exception:
#             raise InternalServerError
#
#
# class SlotApi(Resource):
#     @jwt_required
#     def patch(self, id):
#         try:
#             user_id = get_jwt_identity()
#             body = request.get_json()
#             Slot.objects.get(id=id).update(**body)
#
#             return '', 200
#         except InvalidQueryError:
#             raise SchemaValidationError
#         except DoesNotExist:
#             raise DocumentMissing
#         except Exception:
#             raise InternalServerError
#
#     @jwt_required
#     def delete(self, id):
#         try:
#             user_id = get_jwt_identity()
#             slot = Slot.objects.get(id=id)
#             slot.delete()
#
#             return '', 200
#         except DoesNotExist:
#             raise DocumentMissing
#         except Exception:
#             raise InternalServerError
