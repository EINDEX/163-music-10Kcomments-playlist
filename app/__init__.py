#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import _thread

from flask import Flask
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from pymongo import MongoClient

from app.music import music_init

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

client = MongoClient("mongodb://%s" % os.environ['MONGODB_CONNECTION'])
db = client[os.environ['MONGODB_INSTANCE_NAME']]
songs = db.songs
playlist = db.playlist
music_list = db.list

music_set = set()
username = os.environ['USERNAME']
password = os.environ['PASSWORD']

if __name__ == '__main__':
    _thread.start_new_thread(music_init(),())
    manager.run(app)
