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
from requests import HTTPError

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

playid_url = 'http://music.163.com/api/song/detail/?ids=%s'
comment_url = 'http://music.163.com/weapi/v1/resource/comments/'

headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Referer': 'http://music.163.com/'
}
text = {
    'username': '账号',
    'password': '密码',
    'rememberLogin': 'true'
}


def get_db_conn():
    return pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           password='密码',
                           charset='utf8',
                           db='test',
                           cursorclass=pymysql.cursors.DictCursor)


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
    try:
        url = comment_url + str(ids)
        req_json = requests.post(url, headers=headers, data=data).json()
        if req_json['code'] == 200:
            if 'total' in req_json:
                return req_json['total']
    except IOError as e:
        print(e)
        return
    except HTTPError as e:
        g = Thread(name='消费', target=get_comment, args=(queue,))
        g.start()
        print('打开一个新线程', e)
        return


def get_song_by_playid(queue):
    global playid_id, times
    req_json = requests.get(playid_url % str([ids for ids in range(playid_id, playid_id + 50)])).json()
    if req_json['code'] == 200:
        for song in req_json['songs']:
            times += 1
            if song['commentThreadId'] is not None:
                queue.put(
                    {
                        'id': song['id'],
                        'name': song['name'],
                        'comment_url': song['commentThreadId'],
                        'mp3Url': song['mp3Url'],
                        'mv': song['mvid']
                    })
            print('%s' % times, end='\r')
    playid_id += 50
    with open('play_id.info', 'wt') as info:
        info.write(str(playid_id))


def create_music(q):
    while True:
        get_song_by_playid(q)


def insert(insert_data):
    connection = get_db_conn()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `163music` (`id`, `name`,`mv`,`mp3_url`,`comments`) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql, insert_data)
        connection.commit()
    except pymysql.err.IntegrityError as e:
        print(data, e)
    finally:
        connection.close()


def get_comment(q, ):
    while True:
        global submit_list
        music_dict = q.get()
        ids_comments = get_music_comments(music_dict['comment_url'])
        if ids_comments is None:
            q.put(music_dict)
            time.sleep(60)
            return
        insert_data = (music_dict['id'], music_dict['name'], music_dict['mv'], music_dict['mp3Url'], ids_comments)
        insert(insert_data)


if __name__ == '__main__':
    print('模块', sys.argv[0])
    with open('play_id.info', 'rt') as info:
        playid_id = int(info.read())
    times = 0
    queue = Queue(maxsize=50)
    login()
    c = Thread(name='歌曲信息', target=create_music, args=(queue,))
    c.start()
    for i in range(multiprocessing.cpu_count()):
        g = Thread(name='评论 %s' % i, target=get_comment, args=(queue,))
        g.start()
    c.join()
