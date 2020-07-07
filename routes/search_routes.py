from resources.search import ResultsApi, SuggestionsApi

def search_routes(api):
    api.add_resource(ResultsApi, '/api/results/<search>')
    api.add_resource(SuggestionsApi, '/api/suggestions/<search>')
