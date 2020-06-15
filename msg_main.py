# -*- coding: utf-8 -*-
import socketserver
import threading
from datetime import datetime
from vk_api import *
import time
from termcolor import colored
import colorama
import json
from threading import Thread
from vk_api.utils import get_random_id
from db import User
from utils.mailing import Mailing
from app import app
from configs.texts import MsgTexts

colorama.init()

# {"type": "send_msg", "peer_id": "", "message": "", "attachment": "",
# "forward_messages": "", "sticker_id": "", "keyboard": "", "secret": ""}


fields_send_msg = ['peer_id', 'message', 'attachment', 'forward_messages',
                   'sticker_id', 'keyboard', 'peer_ids', 'user_id', 'user_ids', 'disable_mentions']

secret = app.config['SOCKET_MSG']['msg_module_secret']

mailing = Mailing(app.config['MAILING']['tokens'], app.config['ADMIN_VK_USER_TOKEN'],
                  app.config['MAILING']['album_id'], app.config['GROUP_ID'])


notify_vk_session_msg = VkApi(token=app.config['VK_TOKEN_FOR_NOTIFY_ADMIN'])
vk_notify_msg = notify_vk_session_msg.get_api()


def print_log(string):
    print(f'[{colored("#", "green")}]{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} - {str(string).encode("utf8")}')


def start_mailing(mailing_data, admin_id, mailing_type):
    if mailing_type == 'start_mailing':
        users_obj = iter(User.select().where(User.notify == 1))
    elif mailing_type == 'smart_mailing':
        users_obj = iter(User.select().where(User.last_boost_time < time.time() - 86400, User.notify == 1))
    else:
        users_obj = iter(User.select().where(User.notify == 1))

    users_list = [user.user_id for user in users_obj]

    mailing_responce = mailing.send(users_list, mailing_data)

    vk_notify_msg.messages.send(
        peer_id=admin_id,
        message=MsgTexts.mailing_done % (
            mailing_responce['total'],
            mailing_responce['good'],
            mailing_responce['no_permission'],
            mailing_responce['bad'],
            mailing_responce['time']
        ),
        random_id=get_random_id()
    )


class Service(socketserver.BaseRequestHandler):
    def handle(self):
        print_log('Someone connected')
        while True:
            time.sleep(.1)
            try:
                entered = self.receive()
                try:
                    json_entered = json.loads(entered)
                except json.decoder.JSONDecodeError:
                    json_entered = {}
                # print_log(json_entered)
                if json_entered:
                    if 'secret' in json_entered:
                        if json_entered['secret'] == secret:
                            if json_entered and 'type' in json_entered:
                                if json_entered['type'] == 'start_mailing' or json_entered['type'] == 'smart_mailing':
                                    my_thread = threading.Thread(
                                        target=start_mailing,
                                        args=(
                                            json_entered['mailing_data'],
                                            json_entered['admin_id'],
                                            json_entered['mailing_type'],
                                        )
                                    )

                                    my_thread.start()
                                    # print(json_entered)
                                    self.send('{"response": "ok"}')

                                else:
                                    self.send('{"response": "Error type"}')
                            else:
                                self.send('{"response": "Missing field: type"}')
                        else:
                            self.send('{"response": "Error type"}')
            except ConnectionResetError:
                print_log('Someone disconnected')
                break

    def receive(self, prompt=""):
        self.send(prompt, newline=False)
        return self.request.recv(4096).strip()

    def send(self, string, newline=True):
        if newline:
            string = string + "\n"
        self.request.sendall(string.encode())


class ThreadedService(socketserver.ThreadingMixIn,
                      socketserver.TCPServer,
                      socketserver.DatagramRequestHandler):
    pass


def main():
    port = app.config['SOCKET_MSG']['port']
    host = app.config['SOCKET_MSG']['host']

    service = Service

    server = ThreadedService((host, port), service)
    server.allow_reuse_address = True

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(f'Server started on:\n'
          f'Host: {host}\n'
          f'Port: {port}\n')

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
