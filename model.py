import datetime
import hashlib


from mongoengine import *

#必须使用try except，否则报停止迭代异常
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