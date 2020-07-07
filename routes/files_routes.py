from resources.files import ImageApi

def files_routes(api):
    api.add_resource(ImageApi, '/api/image/<filename>')
