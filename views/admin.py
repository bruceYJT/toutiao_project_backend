import os
import uuid

import jwt

from flask import jsonify, request, send_from_directory
from functools import wraps

from mongoengine import Q

import config
from model import User, Channel, Image
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

# 用户：登录
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

# 用户：获取用户信息
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

# 文章：获取频道
@app.route('/mp/v1_0/channels', methods=["GET"])
def get_channels():
    channels = Channel.objects()
    print(channels.to_public_json())
    return jsonify({
        'massage': 'ok',
        'data':{
            'channels':channels.to_public_json()
        }
    })

# 素材：加载图片文件
@app.route("/images/<string:filename>")
def images_rsp(filename):
    return send_from_directory(config.image_upload_folder, filename)

# 素材：获取素材图片
@app.route("/mp/v1_0/user/images", methods=["GET"])
@login_required
def get_images(userid):
    user = User.objects(id=userid).first()
    collect = request.args.get("collect")
    if collect == 'true':
        imgs = Image.objects(Q(user=user) & Q(isCollect=True))
    elif collect == 'false':
        imgs = Image.objects(user=user)

    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))

    paginated_imgs = imgs.skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "message": 'OK',
        "data": {
            "total_count": imgs.count(),
            "page": page,
            "per_page": per_page,
            "results": paginated_imgs.to_public_json()
        }
    })


# 素材：上传素材图片
@app.route('/mp/v1_0/user/images', methods=["POST"])
@login_required
def upload(userid):
    user = User.objects(id=userid).first()
    image = request.files.get("image")
    if image:
        if not image.filename.endswith(tuple([".jpg", ".png", ".mp4", ".gif"])):
            return jsonify({"error": "Image is not valid"}), 409

        # Generate random filename
        filename = str(uuid.uuid4()).replace("-", "") + "." + image.filename.split(".")[-1]

        if not os.path.isdir(config.image_upload_folder):
            os.makedirs(config.image_upload_folder)

        image.save(os.path.join(config.image_upload_folder, filename))
        img = Image(
            url=filename,
            user=user
        ).save()
    else:
        filename = None

    return jsonify({
        "message": 'OK',
        "data": img.to_public_json()
    })