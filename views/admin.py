import os
import uuid

import jwt

from flask import jsonify, request, send_from_directory
from functools import wraps

from mongoengine import Q

import config
from model import User, Channel, Image, Article, Cover
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
    return jsonify({
        'massage': 'ok',
        'data':{
            'channels':channels.to_public_json()
        }
    })

# w文章：增加文章
@app.route('/mp/v1_0/articles', methods=["POST"])
@login_required
def creat_article(userid):
    draft = request.args.get('draft')
    data = request.json
    cover = Cover(
        type = data.get("cover")['type'],
        images = data.get("cover")['images']
    ).save()
    print(draft)
    if draft == 'false':
        astatus = 2
    else:
        astatus = 0

    article = Article(
        title=data.get('title'),
        user = User.objects(id = userid).first(),
        channel = data['channel_id'],
        content = data['content'],
        covers = cover,
        status = astatus
    ).save()

    return jsonify({
        "message": 'OK'
    })

# 文章：获取全部文章
@app.route("/mp/v1_0/articles", methods=["GET"])
@login_required
def get_articles(userid):
    user = User.objects(id = userid).first()
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    kws = {
        'user':user
    }
    if request.args.get("status") != None:
        kws['status'] = int(request.args.get("status"))
    if request.args.get("channel_id") != None:
        channel = Channel.objects(id = request.args.get("channel_id")).first()
        kws['channel'] = channel
    if request.args.get("begin_pubdate") != None:
        kws['created__gte'] = request.args.get("begin_pubdate")
    if request.args.get("end_pubdate") != None:
        kws['created__lte'] = request.args.get("end_pubdate")
    articles = Article.objects(**kws)
    paginated_articles = articles.skip((page - 1) * per_page).limit(per_page)
    return jsonify({
        "message": 'OK',
        "data": {
            "total_count": articles.count(),
            "page": page,
            "per_page": per_page,
            "results": articles.to_public_json()
        }
    })

# 文章；获取指定文章
@app.route('/mp/v1_0/articles/<string:articleId>', methods=['GET'])
@login_required
def get_article(userid,articleId):
    user = User.objects(id = userid).first()
    article = Article.objects(Q(user=user) & Q(id=articleId)).first()
    return jsonify({
        "message":'OK',
        "data": {
            **article.to_public_json()
        }
    })

# 文章：提交编辑指定文章
@app.route('/mp/v1_0/articles/<string:articleId>', methods=['PUT'])
@login_required
def upload_article(userid,articleId):
    data = request.json
    print(data)
    channel = Channel.objects(id = data.get('channel_id')).first()
    article = Article.objects(id = articleId).first()
    d_cover = article.covers
    cover = Cover(
        type = data.get('cover')['type'],
        images = data.get('cover')['images']
    ).save()
    article.title = data.get('title')
    article.channel = channel
    article.content = data.get('content')
    article.covers = cover
    d_cover.delete()
    article.save()

    return jsonify({
        'message':'ok'
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

# 素材：收藏/删除素材
@app.route("/mp/v1_0/user/images/<string:imageId>", methods=["PUT","DELETE"])
@login_required
def collectImage(userid,imageId):
    print(request.method)
    img = Image.objects(id=imageId).first()
    if request.method == 'PUT':
        img.isCollect = request.json.get('collect')
        img.save()
    elif request.method == 'DELETE':
        img.delete()
    return jsonify({
        "message": 'OK',
        "data": {
            "id": str(img.id),
            "collect": img.isCollect
        }
    })