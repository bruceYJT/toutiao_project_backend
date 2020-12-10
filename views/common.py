

import jwt

from flask import jsonify, request, send_from_directory
from functools import wraps


from app import app

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'Authorization' in request.headers:
            authorization_header = request.headers['Authorization']
            try:
                token = authorization_header.split(' ')[1]
                user = jwt.decode(token, app.config["SECRET_KEY"])
            except:
                return jsonify({"error": "you are not logged in"}), 401
            return f(userid = user['userid'], *args, **kwargs)
        else:
            return jsonify({"error": "you are not logged in"}),401
    return wrap