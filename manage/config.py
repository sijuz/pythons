# -*- coding: utf-8 -*-
class Config:
    DEBUG = True
    USE_VK_SIGN = False
    USE_CORS = True

    CORS = {
        'origins': ['*'],
        'resources': r"/private/*",
        'methods': ['GET']
    }

    VK_APP = {
        'app_secret': '',
        'app_id': 12345
    }

    VK_PARAMS = ['sign', 'vk_user_id']

    MYSQL = {
        'db_name': 'ggcl_mine',
        'user_name': 'ggcl',
        'password': 'XQd7JV42AM',
        'host': '82.202.161.135'
    }

    BONUS = {
        'time': 24 * 60 * 60,
        'case_id': 1
    }

    PAYOUTS = {
        'commission_btc': 50,
        'min_payout': 100,
        'time': 24 * 60 * 60
    }

    ANYPAY = {
        'currency': 'RUB',
        'secret_key': 'test',
        'merchant_id': '0000',
        'anypay_merchant_url': 'https://anypay.io/merchant'
    }

    PAY = {
        149: 75,
        290: 145,
        490: 245,
        990: 495,
        1990: 995,
        3990: 1995
    }

    SOCKET_MSG = {
        'port': 5588,
        'host': '127.0.0.1',
        'msg_module_secret': 'some_secret_code_6281181'
    }

    MAILING = {
        'album_id': 111,
        'tokens': ['', '']
    }

    ADMIN_VK_USER_TOKEN = ''
    GROUP_ID = 111

    VK_TOKEN_FOR_NOTIFY_ADMIN = ''

    SERVER_KEY = ''
    VK_TOKEN_PUBLIC = 'ab7f3060336fdac9ba1b69138588865012093ead18fa248abe3ed87cf16954a174425ab558ec2d40d0501'

    ERROR_IP = '127.0.0.1'

    PROMO_CODES_REF = {
        'from': 10,  # Выдаём 10 рублей создателю промокода
        'to': 500  # Выдаём 500 бизкоинов создателю промокода
    }
