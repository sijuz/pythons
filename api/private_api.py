# -*- coding: utf-8 -*-
from .errors import ApiErrors
from PIL import Image, ImageDraw, ImageFont
from db import User, Farms, Cases, PromoCodes, UsedPromo, Payouts
import time
import sys
import random
from app import app
import hashlib
import io
import codecs
from vk_api import *

sys.path.append("..")

exc = ApiErrors()


def generate_user_info(user_query):
    user_info = {i: getattr(user_query, i) for i in [i for i in list(User.__dict__.keys())
                                                     if not i.startswith('__') and not i.startswith('_')
                                                     and i != 'DoesNotExist' and i != 'id'
                                                     and i != 'user_out' and i != 'user_payouts']}
    user_info['timestamp'] = time.time()
    return user_info


class PrivateApi(object):
    def __init__(self):
        super(PrivateApi, self).__init__()
        self.users = self.Users()
        self.farms = self.Farms()
        self.cases = self.Cases()
        self.promo = self.Promo()
        self.story = self.Story()
        self.games = self.Games()

    class Users(object):
        def __init__(self):
            super(PrivateApi.Users, self).__init__()

        @staticmethod
        def get(data, user_query, method_data):
            """
            GET - api.users.get
            """

            user_query = user_query.get()
            user_hours = (int(time.time()) - user_query.last_boost_time) // (60 * 60)
            if user_hours:
                user_query.balance_bizcoin += user_query.user_performance * user_hours
                user_query.last_boost_time = int(time.time())
                user_query.save()

            user_info = generate_user_info(user_query)
            user_info['balance_new'] = user_query.user_performance * user_hours if user_hours else 0

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'user_info': user_info,
                   }, 200

        @staticmethod
        def balance_ex(data, user_query, method_data):
            """
            GET - api.users.balance_ex
            """

            user_query = user_query.get()

            user_query.balance += round(user_query.balance_bizcoin / 1000, 2)
            user_query.balance_bizcoin = 0
            user_query.save()

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'user_info': generate_user_info(user_query),
                   }, 200

        @staticmethod
        def notify_on(data, user_query, method_data):
            """
            GET - api.users.notify_on
            """

            user_query = user_query.get()

            # user_query.notify = 1
            # user_query.save()

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'user_info': generate_user_info(user_query),
                   }, 200

        @staticmethod
        def notify_off(data, user_query, method_data):
            """
            GET - api.users.notify_off
            """

            user_query = user_query.get()

            # user_query.notify = 0
            # user_query.save()

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'user_info': generate_user_info(user_query),
                   }, 200

        @staticmethod
        def pay_out(data, user_query, method_data):
            """
            GET - api.users.pay_out
            PARAMS:
            sum - сумма выплаты
            type - куда выводить
            wallet - счёт для вывода
            """

            if 'sum' in data and data['sum'] and data['sum'].isdigit() \
                    and 'type' in data and data['type'] \
                    and 'wallet' in data and data['wallet'] and data['wallet'].isdigit() \
                    and data['type'] in ['qiwi', 'ya', 'card'] and data['type'].__len__() <= 50:

                data['sum'] = int(data['sum'])
                data['wallet'] = int(data['wallet'])

                user_query = user_query.get()

                if user_query.balance >= data['sum']:
                    if user_query.balance_bitcoin >= app.config['PAYOUTS']['commission_btc']:

                        user_query.balance -= data['sum']
                        user_query.balance_bitcoin -= app.config['PAYOUTS']['commission_btc']
                        user_query.save()

                        Payouts(
                            user=user_query,
                            sum=data['sum'],
                            type=data['type'],
                            wallet=data['wallet'],
                            ts=time.time()
                        ).save()

                        return {
                                    'status': 'ok',
                                    'method': f'api.{method_data[0]}.{method_data[1]}',
                                    'user_info': generate_user_info(user_query),
                                }, 200
                    else:
                        return exc.return_error(14), 200
                else:
                    return exc.return_error(13), 200
            else:
                return exc.return_error(5, 'sum, type, wallet'), 200

        @staticmethod
        def get_pay_keyboard(data, user_query, method_data):
            """
            GET - api.users.get_pay_keyboard
            """

            def get_url(currency, amount, secret_key, merchant_id, vk_user_id, anypay_merchant_url):
                # Формирование контрольной подписи в форме оплаты
                # Склеиваются параметры currency, amount, секретный ключ, merchant_id и pay_id
                # Разделяются ':'
                # От полученной строки получается md5

                sign_md5 = hashlib.md5(f'{currency}:'
                                       f'{amount}:'
                                       f'{secret_key}'
                                       f':{merchant_id}'
                                       f':{vk_user_id}'.encode('utf-8')).hexdigest()

                anypay_url = f'{anypay_merchant_url}' \
                             f'?currency={currency}' \
                             f'&merchant_id={merchant_id}' \
                             f'&amount={amount}' \
                             f'&pay_id={vk_user_id}' \
                             f'&sign={sign_md5}'

                return anypay_url

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'keyboard_data': {pay_sum: get_url(
                           currency=app.config['ANYPAY']['currency'],
                           amount=pay_sum,
                           secret_key=app.config['ANYPAY']['secret_key'],
                           merchant_id=app.config['ANYPAY']['merchant_id'],
                           vk_user_id=data['vk_user_id'],
                           anypay_merchant_url=app.config['ANYPAY']['anypay_merchant_url']
                       ) for pay_sum in app.config['PAY'].keys()},
                   }, 200

        @staticmethod
        def click(data, user_query, method_data):
            """
            GET - api.users.click
            """
            user_query = user_query.get()
            rr = random.randint(1, 2)
            user_query.balance_bizcoin = user_query.balance_bizcoin + rr
            user_query.save()

            return {
                       'status': 'ok',
                       'plus': rr,
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'user_info': generate_user_info(user_query),
                   }, 200

        @staticmethod
        def get_top(data, user_query, method_data):
            """
            GET - api.users.get_top
            """
            users = User.select().order_by(User.balance_bizcoin.desc()).limit(100)

            vk_session = vk_api.VkApi(token=app.config['VK_TOKEN_PUBLIC'])
            vk = vk_session.get_api()

            users_id = []
            for user in users:
                users_id.append(user.user_id)

            users_vk = vk.users.get(user_ids = users_id,fields = 'photo_100')
            # print(users_vk)
            user_vk_res = []

            for user_vk in users_vk:
                for user in users:
                    if user.user_id == user_vk['id']:
                        user_vk['balance_bizcoin'] = user.balance_bizcoin
                        user_vk_res.append(user_vk)

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'users_top': [{'name': user['first_name'], 'balance_bizcoin': user['balance_bizcoin'],
                                       'photo': user['photo_100']}
                                      for user in user_vk_res],
                   }, 200


    class Farms(object):
        def __init__(self):
            super(PrivateApi.Farms, self).__init__()

        @staticmethod
        def get(data, user_query, method_data):
            """
            GET - api.farms.get
            """

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'farms_data': [{'id': farm.id, 'name': farm.name,
                                       'price': farm.price,
                                       'performance': farm.performance,
                                       'photo_link': farm.photo_link}
                                      for farm in Farms.select().execute()],
                   }, 200

        @staticmethod
        def buy(data, user_query, method_data):
            """
            GET - api.farms.buy
            """
            if data['id'] and data['id'].isdigit:
                bust = Farms.select().where(Farms.id == int(data['id'])).get()

                user_query = user_query.get()
                if user_query.balance >= bust.price:
                    user_query.balance = round(user_query.balance - bust.price, 2)
                    user_query.user_performance += bust.performance
                    user_query.save()

                    return {
                               'status': 'ok',
                               'method': f'api.{method_data[0]}.{method_data[1]}',
                               'user_info': generate_user_info(user_query),
                           }, 200
                else:
                    return exc.return_error(8), 200
            else:
                return exc.return_error(7), 200

    class Cases(object):
        def __init__(self):
            super(PrivateApi.Cases, self).__init__()

        @staticmethod
        def get(data, user_query, method_data):
            """
            GET - api.cases.get
            """

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'cases_data': [{'id': case.id, 'name': case.name,
                                       'price': case.price,
                                       'chance': case.percent * 50000,
                                       'photo_link': case.photo_link}
                                      for case in Cases.select().execute()],
                   }, 200

        @staticmethod
        def buy(data, user_query, method_data):
            """
            GET - api.cases.buy
            """

            def get_money(chance, price):
                r = random.randint(1, 100)
                if chance > r:
                    return random.randint(price * 1000, price * 3000)
                else:
                    return random.randint(100, price * 1000)

            if data['id'] and data['id'].isdigit:
                case = Cases.select().where(Cases.id == int(data['id'])).get()

                user_query = user_query.get()
                if user_query.balance_bitcoin >= case.price:
                    user_query.balance_bitcoin -= case.price
                    win = get_money(case.percent, case.price)
                    user_query.balance_bizcoin += win
                    user_query.save()

                    user_info = generate_user_info(user_query)
                    user_info['case_balance'] = win

                    return {
                               'status': 'ok',
                               'method': f'api.{method_data[0]}.{method_data[1]}',
                               'user_info': user_info,
                           }, 200
                else:
                    return exc.return_error(8), 200
            else:
                return exc.return_error(7), 200

        @staticmethod
        def get_bonus(data, user_query, method_data):
            """
            GET - api.cases.get_bonus
            """
            user_query = user_query.get()

            def get_money(chance, price):
                r = random.randint(1, 100)
                if chance > r:
                    return random.randint(price * 100, price * 300)
                else:
                    return random.randint(100, price * 100)

            if user_query.last_bonus_time + app.config['BONUS']['time'] < time.time():
                case = Cases.select().where(Cases.id == app.config['BONUS']['case_id']).get()

                win = get_money(case.percent, case.price)
                user_query.balance_bizcoin += win
                user_query.last_bonus_time = int(time.time())
                user_query.save()

                user_info = generate_user_info(user_query)
                user_info['case_balance'] = win

                return {
                           'status': 'ok',
                           'method': f'api.{method_data[0]}.{method_data[1]}',
                           'user_info': user_info,
                       }, 200

            else:
                return exc.return_error(9), 200

    class Promo(object):
        def __init__(self):
            super(PrivateApi.Promo, self).__init__()

        @staticmethod
        def use(data, user_query, method_data):
            """
            GET - api.promo.use
            PARAMS:
            promo_code - promo code for btc
            """

            if 'promo_code' in data and data['promo_code'] and data['promo_code'].__len__() < 50:

                if data['promo_code'].__len__() > 2 and data['promo_code'][0] == 'M' \
                        and data['promo_code'].replace('M', '').isdigit():

                    int_id = int(data['promo_code'].replace('M', ''))
                    user_query = User.select().where(User.user_id == int_id)
                    if user_query.exists():
                        user_query = user_query.get()
                        user_query_ref = User.select().where(User.user_id == data['vk_user_id']).get()
                        if not user_query.ref_status:
                            if user_query.balance_bitcoin < app.config['PAYOUTS']['commission_btc'] - 5:
                                user_query.balance_bitcoin += app.config['PROMO_CODES_REF']['from']
                                user_query.save()

                            user_query_ref.balance_bizcoin += app.config['PROMO_CODES_REF']['to']
                            user_query_ref.ref_status = 1
                            user_query_ref.save()

                            return {
                                       'status': 'ok',
                                       'method': f'api.{method_data[0]}.{method_data[1]}',
                                       'user_info': generate_user_info(user_query_ref),
                                       'balance_bizcoin_up': app.config['PROMO_CODES_REF']['from']
                                   }, 200
                        else:
                            return exc.return_error(19), 200

                    else:
                        return exc.return_error(10), 200
                else:
                    promo_query = PromoCodes.select().where(PromoCodes.code == data['promo_code'])
                    if promo_query.exists():
                        promo_query = promo_query.get()
                        if promo_query.use_count > 0:
                            user_query = user_query.get()
                            used_promo_code = UsedPromo.select().where(UsedPromo.promo_code == promo_query,
                                                                       UsedPromo.user == user_query)

                            if not used_promo_code.exists():
                                user_query.balance_bizcoin += promo_query.bonus
                                user_query.save()

                                promo_query.use_count -= 1
                                promo_query.save()

                                UsedPromo(
                                    promo_code=promo_query,
                                    user=user_query,
                                    to_balance_bizcoin=promo_query.bonus,
                                    ts=time.time()
                                ).save()

                                return {
                                           'status': 'ok',
                                           'method': f'api.{method_data[0]}.{method_data[1]}',
                                           'user_info': generate_user_info(user_query)
                                       }, 200
                            else:
                                return exc.return_error(12), 200

                        else:
                            return exc.return_error(11), 200
                    else:
                        return exc.return_error(10), 200
            else:
                return exc.return_error(1, 'promo_code'), 200

    class Story(object):
        def __init__(self):
            super(PrivateApi.Story, self).__init__()

        @staticmethod
        def get_photo_balance(data, user_query, method_data):
            """
            GET - api.story.get_photo_balance
            """
            user_query = user_query.get()

            # if user_query.last_story_time + 60*60 < time.time():
            #     user_query.last_story_time = time.time()
            #     user_query.save()

            text = f'{user_query.balance_bizcoin} $'

            width, height = (1080, 220)
            im = Image.new("RGBA", (width, height))
            draw = ImageDraw.Draw(im)

            font = ImageFont.truetype("res/GothaProMed.otf", 160)

            draw.text(((width / 2) - len(text) * 50, (height / 2) - 40), text, (255, 255, 255), font=font)

            img_bytes = io.BytesIO()
            im.save(img_bytes, format='PNG')
            base64_data = codecs.encode(img_bytes.getvalue(), 'base64')
            base64_text = codecs.decode(base64_data, 'ascii')

            return {
                       'status': 'ok',
                       'method': f'api.{method_data[0]}.{method_data[1]}',
                       'photo': 'data:image/png;base64,' + base64_text.replace('\n', '')
                   }, 200
            # else:
            #     return exc.return_error(16, f'{60*60} sec'), 200

    class Games(object):
        def __init__(self):
            super(PrivateApi.Games, self).__init__()

        @staticmethod
        def wheel_of_fortune(data, user_query, method_data):
            """
            GET - api.games.wheel_of_fortune
            """
            user_query = user_query.get()

            if user_query.balance_bizcoin >= 3000:
                wheel_list = ['diamond_500'] * 20 + \
                             ['diamond_1500'] * 20 + \
                             ['rub_20'] * 10 + \
                             ['booster_2'] * 3 + \
                             ['diamond_5000'] * 25 + \
                             ['diamond_15000'] * 18 + \
                             ['booster_5'] * 1 + \
                             ['rub_500'] * 3

                random_choice = random.choice(wheel_list)

                if random_choice.startswith('diamond_'):
                    user_query.balance_bizcoin += int(random_choice[8:])

                elif random_choice.startswith('rub_'):
                    user_query.balance += int(random_choice[4:])

                elif random_choice.startswith('booster_'):
                    bust = Farms.select().where(Farms.id == int(random_choice[8:])).get()
                    user_query.user_performance += bust.performance

                user_query.balance_bizcoin -= 3000
                user_query.save()

                return {
                           'status': 'ok',
                           'method': f'api.{method_data[0]}.{method_data[1]}',
                           'user_info': generate_user_info(user_query),
                           'gift': random_choice
                       }, 200
            else:
                return exc.return_error(13), 200

    def process(self, category, method, data):
        if hasattr(self, category):
            if hasattr(getattr(self, category), method):
                vk_user_id = int(data['vk_user_id'])
                user_query = User.select().where(User.user_id == vk_user_id)
                if not user_query.exists():
                    User(user_id=vk_user_id,
                         user_ts=int(time.time()),
                         last_boost_time=int(time.time())).save()
                # user_query = user_query.get()

                return getattr(getattr(self, category), method)(
                    data, user_query, (category, method))

            else:
                return exc.return_error(2, method), 200
        else:
            return exc.return_error(3, category), 200
