import binascii
import threading

import requests
import json
import os
import base64
import time

from Crypto.Cipher import AES
from app import db, music_set, username, password, songs, music_list, playlist

song_url = 'http://music.163.com/api/song/detail/?ids=%s'


def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext).decode('u8')
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return binascii.hexlify(os.urandom(size))[:16]


def login():
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5f' \
              'f68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629' \
              'ec4ee341f56135fccf695280104e0312ecbda92557c93870' \
              '114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424' \
              'd813cfe4875d3e82047b97ddef52741d546b8e289dc6935b' \
              '3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'
    text = {
        'username': username,
        'password': password,
        'rememberLogin': 'true'
    }
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)

    return {
        'params': encText,
        'encSecKey': encSecKey
    }


class MusicGet(threading.Thread):
    def __init__(self):
        super().__init__()
        self.data = login()
        playlist_id = db['playlist'].find_one({'_id': 'playlist'})
        if playlist_id is None:
            db['playlist'].insert({'_id': 'playlist', 'id': 100001})
        for song in db['songs'].find():
            music_set.add(song['id'])

    def run(self):
        playlist_url = 'http://music.163.com/api/playlist/detail?id=%s'
        comment_url = 'http://music.163.com/weapi/v1/resource/comments/%s'
        headers = {
            'Cookie': 'appver=1.5.0.75771;',
            'Referer': 'http://music.163.com/'
        }
        while True:
            playlist_id = db['playlist'].find_one({'_id': 'playlist'})['id']
            req_json = requests.get(playlist_url % str(playlist_id)).json()
            if req_json['code'] == 200:
                req_json['_id'] = req_json['result']['id']
                for song in req_json['result']['tracks']:
                    if song['id'] not in music_set:
                        music_set.add(song['id'])
                        try:
                            ids_comments = requests.post(comment_url % song['commentThreadId'], headers=headers,
                                                         data=self.data).json()
                            if ids_comments['code'] == 200:
                                song['comments'] = ids_comments['hotComments']
                                song['comment_total'] = ids_comments['total']
                                song['_id'] = song['id']
                                songs.save(song)
                                print(song)
                        except TimeoutError and ConnectionError:
                            time.sleep(30)
                music_list.save(req_json)
            playlist.update({'_id': 'playlist'}, {'$inc': {'id': 1}})
