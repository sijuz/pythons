# -*- coding: utf-8 -*-
class ApiErrors:
    def __init__(self):
        api_text = 'API Error: '
        self.errors_dict = errors_dict = {
            # Server default errors
            500: {
                "error": f"{api_text}Internal server error",
                "code": 500
            },
            404: {
                "error": f"{api_text}Not Found",
                "code": 404
            },
            405: {
                "error": f"{api_text}Method is not allowed(POST or GET)",
                "code": 405
            },

            # Custom API errors
            1: {
                "error": f"{api_text}Missed %s param",
                "code": 1
            },
            2: {
                "error": f"{api_text}Wrong method; You use: %s",
                "code": 2
            },
            3: {
                "error": f"{api_text}Wrong category; You use: %s",
                "code": 3
            },
            4: {
                "error": f"{api_text}%s must be integer",
                "code": 4
            },
            5: {
                "error": f"{api_text}One param missed or invalid: need %s",
                "code": 5
            },
            6: {
                "error": f"{api_text}Invalid sign or insufficient parameters for check sign",
                "code": 6
            },
            7: {
                "error": "Ускоритель не найден",
                "code": 7
            },
            8: {
                "error": "Недостаточно средств",
                "code": 8
            },
            9: {
                "error": f"{api_text}last time error",
                "code": 9
            },
            10: {
                "error": "Промокод не существует",
                "code": 10
            },
            11: {
                "error": "Лимит промокода исчерпан",
                "code": 11
            },
            12: {
                "error": "Промокод уже использован",
                "code": 12
            },
            13: {
                "error": f"{api_text}Not enough money on output balance",
                "code": 13
            },
            14: {
                "error": f"{api_text}Not enough money on bitcoin balance(commission for payout)",
                "code": 14
            },
            15: {
                "error": f"{api_text}Too many payouts. Server allow one payout in %s",
                "code": 15
            },
            16: {
                "error": f"{api_text}Too many story publications. Server allow one story publications in %s",
                "code": 16
            },
            17: {
                "error": f"{api_text}Can not load JSON from data",
                "code": 17
            },
            18: {
                "error": f"{api_text}Vzlom jopi",
                "code": 18
            },
            19: {
                "error": f"Вы уже активировали промокод от другого пользователя",
                "code": 19
            }
        }

    def return_error(self, code, *args):
        return {
            'error': self.errors_dict[code]['error'] % args,
            'code': self.errors_dict[code]['code']
        }
