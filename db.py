# -*- coding: utf-8 -*-
from flask import request
from peewee import MySQLDatabase, Model, CharField, IntegerField, BooleanField, ForeignKeyField, FloatField, TextField
from app import app
import peeweedbevolve


db = MySQLDatabase(
    app.config['MYSQL']['db_name'], user=app.config['MYSQL']['user_name'],
    password=app.config['MYSQL']['password'],
    host="82.202.161.135"
)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    @property
    def balance(self):
        return self._balance_rub

    @balance.setter
    def balance(self, value):
        self._balance_rub = round(value, 2)

    user_id = IntegerField(unique=True)  # id пользователя

    _balance_rub = FloatField(default=0.00)  # Баланс алмазы
    balance_bizcoin = IntegerField(default=0)  # Баланс bizcoin уголь
    balance_bitcoin = IntegerField(default=0)  # Баланс bitcoin золото
    balance_bitcoin2 = IntegerField(default=0)  # Баланс bitcoin железо
    user_performance = IntegerField(default=100)  # Доход bizcoin/час

    last_boost_time = IntegerField(default=0)  # Указывается время списание бустеров - time.time()
    user_ts = IntegerField(default=0)  # ts регистрации
    last_bonus_time = IntegerField(default=0)  # ts выдачи бонуса
    last_story_time = IntegerField(default=0)  # ts публикации истории

    notify = BooleanField(default=0)  # Состояние подписки на сообщения сообщества

    ref_status = BooleanField(default=0)


class Farms(BaseModel):
    name = CharField(default='')  # Название бустера
    price = IntegerField(default=0)  # Цена бустера
    performance = IntegerField(default=0)  # Доход bizcoin/час
    photo_link = CharField(default='')  # Ссылка на фото фермы


class Cases(BaseModel):
    name = CharField(default='')  # Название кейса
    price = IntegerField(default=0)  # Цена кейса
    percent = IntegerField(default=0)  # Шанс выпадения
    photo_link = CharField(default='')  # Ссылка на фото кейса


class PromoCodes(BaseModel):
    code = CharField(default='')  # Название кейса
    bonus = IntegerField(default=0)  # Цена кейса
    use_count = IntegerField(default=1)  # Шанс выпадения


class UsedPromo(BaseModel):
    promo_code = ForeignKeyField(PromoCodes, backref='prom_out')
    user = ForeignKeyField(User, backref='user_out')
    to_balance_bizcoin = IntegerField(default=0)
    ts = IntegerField(default=0)


class Payouts(BaseModel):
    user = ForeignKeyField(User, backref='user_payouts')
    sum = IntegerField(default=0)
    type = CharField(default='')
    wallet = IntegerField(default=0)
    ts = IntegerField(default=0)
    # paid - выплачено, exit - отменено, moder - модерация
    status = CharField(default='moder')


class Games(BaseModel):
    name = CharField(default='')  # Название кейса
    price = CharField(default='')  # Цена
    photo_link = CharField(default='')  # Ссылка на фото
    json_data = TextField()


@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

    


@app.after_request
def after_request(response):
    if request.path == '/favicon.ico':
        ...
    elif request.path.startswith('/static'):
        ...

    if not db.is_closed():
        db.close()

    return response
