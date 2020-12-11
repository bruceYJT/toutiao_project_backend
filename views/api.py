import os
import uuid
from datetime import datetime

import jwt

from flask import jsonify, request, send_from_directory
from functools import wraps

from mongoengine import Q

import config
from model import User, Channel, Image, Article, Cover
from werkzeug.security import generate_password_hash, check_password_hash

from app import app

from .common import login_required

# 用户：登录
@app.route("/app/v1_0/authorizations", methods=["POST"])
def app_login():
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

@app.route("/app/v1_0/user")
@login_required
def get_user_info(userid):
    userinfo = User.objects(id=userid).first()
    if not userinfo:
        return jsonify({"message": "Invalid user."})
    else:
        return jsonify({
            "message": 'OK',
            "data": {
                "name": userinfo.name,
                "photo": userinfo.photo,
                "is_media": False,
                "intro": userinfo.intro,
                "certi": "",
                "art_count": 5,
                "follow_count": 5,
                "fans_count": 5,
                "like_count": 5,
                "id": str(userinfo.id)
            }
        })

@app.route("/app/v1_0/channels", methods=["GET"])
@login_required
def client_get_channels(userid):

    channels = Channel.objects()

    return jsonify({
        "message": 'OK',
        "data": {
            "channels": channels.to_public_json()
        }
    })

@app.route("/app/v1_0/user/channels", methods=["PATCH"])
@login_required
def user_add_channel(userid):
    user = User.objects(id=userid).first()
    body = request.json
    channels = body.get('channels')
    channel_id = channels[0]['id']
    channel_add = Channel.objects(id=channel_id).first()
    user.channels.append(channel_add)
    user.save()
    return jsonify({
        "message": 'OK',
        "data": {}
    })

@app.route("/app/v1_0/user/channels", methods=["GET"])
@login_required
def get_user_channels(userid):
    user = User.objects(id=userid).first()

    return jsonify({
        "message": 'OK',
        "data": {
            "channels":[channel.to_public_json() for channel in user.channels]
        }
    })

@app.route("/app/v1_0/user/channels/<string:channelid>", methods=["DELETE"])
@login_required
def delete_user_channel(userid,channelid):
    user = User.objects(id=userid).first()
    channel_del = Channel.objects(id=channelid).first()
    user.channels.remove(channel_del)
    user.save()

    return jsonify({
        "message": 'OK',
        "data": {}
    })

def datatime2timestamp(_date):
    millisec = _date.timestamp() * 1000
    return int(millisec)

def timestamp2datatime(_timestamp):
        d = datetime.fromtimestamp(_timestamp / 1000)
        return d

@app.route("/app/v1_1/articles", methods=["GET"])
@login_required
def get_articles_by_channelid(userid):
    page = 1
    per_page = 10
    param = request.args
    query_timestamp = param.get('timestamp')
    channel_id = param.get('channel_id')
    refresh = param.get('refresh')
    print(refresh)
    _date = timestamp2datatime(int(query_timestamp))
    if refresh == 1:
        articles = Article.objects(Q(channel=channel_id)&Q(created__gt=_date)).order_by("-created")
        print(len(articles))
        paginated_articles = articles.skip(len(articles)-10).limit(per_page)
    else:
        articles = Article.objects(Q(channel=channel_id)&Q(created__lt=_date)).order_by("-created")
        paginated_articles = articles.skip((page - 1) * per_page).limit(per_page)
        print(len(articles))
    if len(paginated_articles) <= 0:
        return jsonify({
            "message": 'OK',
            "data": {
                "pre_timestamp": 0,
                "total_count": articles.count(),
                "page": page,
                "per_page": per_page,
                "results": []
            }
        })
    else:
        pre_timestamp = datatime2timestamp(paginated_articles[len(paginated_articles) - 1].created)
        print(pre_timestamp)
        return jsonify({
                "message": 'OK',
                "data": {
                    "pre_timestamp": pre_timestamp,
                    "total_count": articles.count(),
                    "page": page,
                    "per_page": per_page,
                    "results": paginated_articles.to_public_json_client()
                }
            })


    # 文章搜素功能接口的设想，考虑到大量文章的搜索功能优化问题，改用elasticsearch来单独改进文章搜索（存储标题和文章id），再通过其id查询mongodb查询文章详细数据。