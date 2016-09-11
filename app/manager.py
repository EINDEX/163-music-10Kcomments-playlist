#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading

from app import manager, app
from music import MusicGet

if __name__ == '__main__':
    music_get = MusicGet()
    manager.run(app)