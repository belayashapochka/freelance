from peewee import *


db = SqliteDatabase('database/database.db')


class BaseModel(Model):
    id = IntegerField(unique=True, primary_key=True)

    class Meta:
        database = db
        order_by = 'id'


class UserTg(BaseModel):
    name = CharField()
    tgName = CharField()
    tgId = CharField(unique=True)
    phone = CharField()
    company = CharField(null=True)
    isAuth = BooleanField(default=False)
    lastAuction = BooleanField(default=False)

    class Meta:
        db_table = 'UsersTg'


class Auction(BaseModel):
    auctionId = IntegerField(unique=True)
    title = CharField()
    description = CharField()
    weight = FloatField()
    price = IntegerField()
    timeStart = CharField()
    timeDelay = IntegerField()
    payType = CharField()
    sendGif = BooleanField()
    sendPhoto = BooleanField()
    winner = CharField(null=True)


class Rate(BaseModel):
    auctionId = IntegerField()
    date = DateTimeField(unique=True)
    company = CharField()
    bet = IntegerField()


'''
with db:
    db.create_tables([Auction,UserTg,Rate])
'''