# -*- coding: utf-8 -*-
class Config:
    DEBUG = False
    USE_VK_SIGN = True
    USE_CORS = True

    CORS = {
        'origins': ['*'],
        'resources': r"/private/*",
        'methods': ['GET']
    }

    VK_APP = {
        'app_secret': 'N2P2VfdTdxaXYqW8Cd9b',
        'app_id': 7504408
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
        'commission_btc': 75,
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
        'msg_module_secret': 'shDH91GHA821hZmjQibzgfayt1SF71b1fArf'
    }

    MAILING = {
        'album_id': 265893656,
        'tokens': ['ab7f3060336fdac9ba1b69138588865012093ead18fa248abe3ed87cf16954a174425ab558ec2d40d0501', '']
    }

    ADMIN_VK_USER_TOKEN = '3007f0edb3fb9dd3deea2d9dd5542b7fc887b1448cea7012f3377efd66444c52bb6ca4140a803237ee2a6'
    GROUP_ID = 186104500

    VK_TOKEN_FOR_NOTIFY_ADMIN = '3007f0edb3fb9dd3deea2d9dd5542b7fc887b1448cea7012f3377efd66444c52bb6ca4140a803237ee2a6'
    
    VK_TOKEN_PUBLIC = 'ab7f3060336fdac9ba1b69138588865012093ead18fa248abe3ed87cf16954a174425ab558ec2d40d0501'

    SERVER_KEY = ''

    ERROR_IP = '127.0.0.1'

    PROMO_CODES_REF = {
        'from': 2,  # Выдаём 2 золота создателю промокода
        'to': 500  # Выдаём 500 бизкоинов создателю промокода
    }
