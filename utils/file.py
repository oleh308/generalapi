import os
from app import app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(filename, file):
    if allowed_file(filename):
        filename = secure_filename(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return True
    else:
        return False
