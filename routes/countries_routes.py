from resources.country import CountriesApi, CountryApi

def countries_routes(api):
    api.add_resource(CountriesApi, '/api/countries')
    api.add_resource(CountryApi, '/api/countries/<id>')
