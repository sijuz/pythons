# -*- coding: utf-8 -*-
from flask import request, send_file
from app import app

from api.private_api import PrivateApi
from api.errors import ApiErrors
from db import User

from utils.vkpass import is_valid
from utils.nc import NetCat
from utils.mailing import Mailing

import hashlib
import json
import requests
import socket

exc = ApiErrors()
private_api = PrivateApi()

# nc = NetCat(app.config['SOCKET_MSG']['host'], app.config['SOCKET_MSG']['port'])
#
# mailing = Mailing(app.config['MAILING']['tokens'], app.config['ADMIN_VK_USER_TOKEN'],
#                   app.config['MAILING']['album_id'], app.config['GROUP_ID'])


# @app.route('/send_mailing', methods=["POST"])
# def send_mailing():
#     # noinspection PyBroadException
#     try:
#         data = json.loads(request.data)
#     except Exception as e:
#         # Can not load JSON from data
#         return exc.return_error(17)
#
#     if 'key' in request.values and request.values['key'] and request.values['key'] == app.config['SERVER_KEY'] \
#             and 'type' in request.values and request.values['type'] \
#             and request.values['type'] in ['start_mailing', 'smart_mailing']:
#
#         if 'reply_message' in data['object']['message'].keys():
#
#             if data['object']['message']['reply_message']:
#                 mailing_obj = data['object']['message']['reply_message']
#             else:
#                 mailing_obj = data['object']['message']
#
#         elif data['object']['message']['fwd_messages']:
#             mailing_obj = data['object']['message']['fwd_messages'][0]
#
#         else:
#             mailing_obj = data['object']['message']
#
#         mailing_data = mailing.generate_data(mailing_obj)
#
#         to_send = {
#             "type": request.values['type'],
#             "secret": app.config['SOCKET_MSG']['msg_module_secret'],
#             "mailing_type": 'global_mailing',
#             "mailing_data": mailing_data,
#             "admin_id": data['object']['message']['peer_id']
#         }
#
#         nc.write(json.dumps(to_send).encode())
#         nc.read()
#
#         return {'status': 'ok'}
#     else:
#         return exc.return_error(18)
#

@app.route('/', methods=["GET"])
def index():
    return {'status': 'ok'}


@app.route('/morgen', methods=['GET'])
def morgen():
    return send_file('res/morgen.mp4', attachment_filename='morgen.mp4')


@app.route('/private/api.<string:category>.<string:method>', methods=['GET'])
def private_api_handler(category, method):
    data = dict(request.values)

    if app.config['USE_VK_SIGN']:
        # Проверка подписи ВК
        if all(item in data.keys() for item in app.config['VK_PARAMS']):
            if is_valid(query=data, secret=app.config['VK_APP']['app_secret']):
                return private_api.process(category.lower(), method.lower(), data)
            else:
                requests.post(f'http://{app.config["ERROR_IP"]}/report', data=json.dumps({
                    "key": app.config['ERROR_KEY'],
                    "error": f"ERROR VK SIGN: {data}",
                    "host": str(socket.gethostbyname(socket.gethostname()))
                }))
                return exc.return_error(6), 200
        else:
            requests.post(f'http://{app.config["ERROR_IP"]}/report', data=json.dumps({
                "key": app.config['ERROR_KEY'],
                "error": f"ERROR VK SIGN: {data}",
                "host": str(socket.gethostbyname(socket.gethostname()))
            }))
            return exc.return_error(6), 200
    else:
        return private_api.process(category.lower(), method.lower(), data)


@app.route('/pay', methods=['POST'])
def pay():
    if 'merchant_id' in request.values \
            and 'amount' in request.values \
            and 'pay_id' in request.values \
            and 'pay_date' in request.values \
            and 'sign' in request.values:

        '''
        Формирование контрольной подписи в обработчике
        Формирование подписи производится путем склеивания
        параметров через ":" и создание контрольной суммы MD5.
        Склеиваются параметры merchant_id, amount, pay_id и секретный ключ.
        '''

        sign_md5 = hashlib.md5(f"{app.config['ANYPAY']['merchant_id']}:{request.values['amount']}"
                               f":{request.values['pay_id']}:{app.config['ANYPAY']['secret_key']}"
                               .encode('utf-8')).hexdigest()

        if sign_md5 == request.values['sign']:
            query = User.select().where(User.user_id == request.values['pay_id'])
            amount = int(request.values['amount'])
            if amount in app.config['PAY'].keys() and query.exists():
                query = query.get()
                query.balance_bitcoin += app.config['PAY'][amount]
                query.save()

            return 'OK'
        else:
            return 'Bad sign'
    else:
        return 'Invalid params'
