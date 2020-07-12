from resources.calendar import CalendarsApi, CalendarSlotApi, CalendarSlotsApi

def calendar_routes(api):
    api.add_resource(CalendarsApi, '/api/calendars')
    api.add_resource(CalendarSlotsApi, '/api/calendars/<id>/slots')
    api.add_resource(CalendarSlotApi, '/api/calendars/<id>/slots/<slot_id>')
