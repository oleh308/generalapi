from flask_restful import Resource
from flask import send_from_directory

class ImageApi(Resource):
    def get(self, filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
