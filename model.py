import datetime
import hashlib


from mongoengine import *

#必须使用try except，否则报停止迭代异常
import config


class CustomQuerySet(QuerySet):
    def to_public_json(self):
        result = []
        try:
            for doc in self:
                json = doc.to_public_json()
                result.append(json)
        except:
            print('error')

        return result


connect("yesthday_toutiao")

class User(Document):
    mobile = StringField(max_length=11, unique=True)
    name = StringField(required=True, unique=True)
    code = StringField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    photo = StringField(required=True)
    gender = IntField(required=True)
    intro = StringField(required=True)
    email = StringField(required=True, unique=True)

    def to_public_json(self):
        data = {
            "mobile": self.mobile,
            "name": self.name,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "photo": self.photo,
            "gender": self.gender,
            "intro": self.intro,
            'email': self.email
        }

        return data

class Channel(Document):
    name = StringField(max_length=120,required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            'id': str(self.id),
            'name': self.name,
        }

        return data

class Cover(Document):
    url = StringField(max_length=300, required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            "message":"文件上传成功",
            "data": {
                "id": str(self.id),
                "url": '/file/' + self.url,
            },
        }

        return data


class Article(Document):
    title = StringField(max_length=120, required=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    channel = ReferenceField(Channel, reverse_delete_rule=CASCADE)
    content = StringField(max_length=5000)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    covers = ListField(ReferenceField(Cover, reverse_delete_rule=CASCADE))
    status = IntField(required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
        'title':self.title,
        'content':self.content,
        "cover": [{
            "id": str(cover.id),
            "url": '/file/' + cover.url
        } for cover in self.covers],
        'channel_id': self.channel.id
      }

        return data

class Image(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    url = StringField(max_length=300, required=True)
    isCollect = BooleanField(required=True,default=False)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
        'id':str(self.id),
        'user':self.user.name,
        'url':config.base_url + 'images/' + self.url,
        'is_collected': self.isCollect
      }

        return data
