#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap, ConditionalCDN, WebCDN, JQUERY_VERSION, BOOTSTRAP_VERSION, HTML5SHIV_VERSION, \
    RESPONDJS_VERSION
from flask.ext.moment import Moment
from pymongo import MongoClient

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


def change_cdn_domestic(tar_app):
    static = tar_app.extensions['bootstrap']['cdns']['static']
    local = tar_app.extensions['bootstrap']['cdns']['local']

    def change_one(tar_lib, tar_ver, fallback):
        tar_js = ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', fallback,
                                WebCDN('//cdn.bootcss.com/' + tar_lib + '/' + tar_ver + '/'))

        tar_app.extensions['bootstrap']['cdns'][tar_lib] = tar_js

    libs = {'jquery': {'ver': JQUERY_VERSION, 'fallback': local},
            'bootstrap': {'ver': BOOTSTRAP_VERSION, 'fallback': local},
            'html5shiv': {'ver': HTML5SHIV_VERSION, 'fallback': static},
            'respond.js': {'ver': RESPONDJS_VERSION, 'fallback': static}}
    for lib, par in libs.items():
        change_one(lib, par['ver'], par['fallback'])


change_cdn_domestic(app)

client = MongoClient("mongodb://%s" % os.environ['MONGODB_CONNECTION'])
db = client[os.environ['MONGODB_INSTANCE_NAME']]
songs = db.songs
playlist = db.playlist
music_list = db.list

music_set = set()
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
