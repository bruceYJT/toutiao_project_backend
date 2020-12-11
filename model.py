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

    def to_public_json_client(self):
        result = []
        try:
            for doc in self:
                jsonDic = doc.to_public_json_client()
                result.append(jsonDic)
        except:
            print('error')

        return result

connect("yesthday_toutiao")

class Channel(Document):
    name = StringField(max_length=120,required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            'id': str(self.id),
            'name': self.name,
        }

        return data


class User(Document):
    mobile = StringField(max_length=11, unique=True)
    name = StringField(required=True, unique=True)
    code = StringField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    photo = StringField(required=True)
    gender = IntField(required=True)
    intro = StringField(required=True)
    email = StringField(required=True, unique=True)
    channels = ListField(ReferenceField(Channel))

    def to_public_json(self):
        data = {
            "id": str(self.id),
            "mobile": self.mobile,
            "name": self.name,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "photo": self.photo,
            "gender": self.gender,
            "intro": self.intro,
            'email': self.email
        }

        return data

class Cover(Document):
    type = IntField(required=True)
    images = ListField(StringField(max_length=200))

    def to_public_json(self):
        data = {
            'type':self.type,
            'images':self.images
        }

        return data


class Article(Document):
    title = StringField(max_length=120, required=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    channel = ReferenceField(Channel, reverse_delete_rule=CASCADE)
    content = StringField(max_length=5000)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    covers = ReferenceField(Cover)
    status = IntField(required=True)
    user_collect = ListField(ReferenceField(User, reverse_delete_rule=CASCADE))
    is_collected = BooleanField(required=False)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            'id':str(self.id),
            'title':self.title,
            'status':self.status,
            'pubdate':self.created.strftime('%Y-%m-%d %H:%M'),
            "cover": self.covers.to_public_json(),
            'content': self.content,
            'channel_id': str(self.channel.id)
        }

        return data

    def to_public_json_client(self):
        data = {
            "art_id": str(self.id),
            "status": self.status,
            "title" : self.title,
            "pubdate":self.created,
            "aut_name":self.user.name,
            "aut_id":str(self.user.id),
            "content":self.content,
            "is_collected":self.is_collected,
            "cover":self.covers.to_public_json()
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


if __name__ == '__main__':
    channel = Channel.objects(id='5fc9aa475b0649bb175dbaab').first()
    user = User.objects().first()
    cover = Cover.objects().first()
    for i in range(33):
        print(i)
        article = Article(
            title=f"ArticleArticleArticle{i}",
            channel=channel,
            content=f"ArticleArticleArticlecontentcontentcontent{i+50}",
            user=user,
            covers=cover,
            status=2,
            created=datetime.datetime.now()
        ).save()