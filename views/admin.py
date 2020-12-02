import jwt

from flask import jsonify, request
from functools import wraps
from model import User
from werkzeug.security import generate_password_hash, check_password_hash

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


@app.route("/mp/v1_0/authorizations", methods=["POST"])
def login():
    if not request.json.get("mobile"):
        return jsonify({"error": "mobile not specified"}), 409
    if not request.json.get("code"):
        return jsonify({"error": "code not specified"}), 409

    try:
        mobile = request.json.get("mobile")
        print(mobile)
        users = User.objects(mobile=mobile)
    except:
        print('error')

    user = users.first()

    if user == None:
        return jsonify({"error": "User not found"}), 403



    if not check_password_hash(user.code, request.json.get("code")):
        return jsonify({"error": "Invalid code"}), 401

    token = jwt.encode({
        "userid": str(user.id),
        "username": user.name,
        "email": user.email,
        "created": str(user.created)
    }, app.config["SECRET_KEY"])

    return jsonify({
        # "success": True,
        "message": '登录成功',
        "data": {
            "user": user.name,
            "token": token.decode("UTF-8")
            # "email": user.email,
            # "password": user.password,
            # "created": str(user.created)
        },

    })


@app.route("/mp/v1_0/user/profile", methods=["GET"])
@login_required
def get_user_profile(userid):
    # 数据库查找信息
    user = User.objects(id=userid).first()
    # 返回数据
    return jsonify({
        'massage': 'ok',
        'data':user.to_public_json()
    })