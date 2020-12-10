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