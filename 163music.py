import binascii
import multiprocessing
import pymysql
import requests
import json
import os
import base64
import time
import sys

from Crypto.Cipher import AES
from queue import Queue
from threading import Thread

from pymongo import MongoClient
from requests import HTTPError

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

song_url = 'http://music.163.com/api/song/detail/?ids=%s'
comment_url = 'http://music.163.com/weapi/v1/resource/comments/'

headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Referer': 'http://music.163.com/'
}
text = {
    'username': os.environ['USERNAME'],
    'password': os.environ['PASSWORD'],
    'rememberLogin': 'true'
}

client = MongoClient()
db = client['163music']
song_id = 60000


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
    global text, data
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }


def get_music_comments(ids):
    """获取评论"""
    time.sleep(500)
    url = comment_url + str(ids)
    req_json = requests.post(url, headers=headers, data=data).json()
    return req_json


def get_song_by_playid(queue):
    global song_id, times
    req_json = requests.get(song_url % str([ids for ids in range(song_id, song_id + 50)])).json()
    if req_json['code'] == 200:
        for song in req_json['songs']:
            if song['commentThreadId'] is not None:
                queue.put(
                    {
                        'id': song['id'],
                        'name': song['name'],
                        'comment_url': song['commentThreadId'],
                        'mp3Url': song['mp3Url'],
                        'mv': song['mvid']
                    })
    song_id += 50


def create_music(q):
    while True:
        get_song_by_playid(q)


def insert(insert_data):
    print(insert_data)
    songs = db.songs
    songs.update({'_id': insert_data['id']}, insert_data, True)


def get_comment(q, ):
    while True:
        music_dict = q.get()
        ids_comments = get_music_comments(music_dict['comment_url'])
        if ids_comments is None:
            return
        music_dict['comments'] = ids_comments['hotComments']
        music_dict['comment_total'] = ids_comments['total']
        insert(music_dict)


if __name__ == '__main__':
    print('模块', sys.argv[0])
    queue = Queue(maxsize=50)
    login()
    c = Thread(name='歌曲信息', target=create_music, args=(queue,))
    c.start()
    for i in range(multiprocessing.cpu_count()):
        g = Thread(name='评论 %s' % i, target=get_comment, args=(queue,))
        g.start()
    c.join()
