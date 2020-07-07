import ssl
from flask_mongoengine import MongoEngine

db = MongoEngine()

def initialize_db(app):
    db.connect(host=app.config["MONGO_URI"], ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
