#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from flask import render_template

from app import app, manager


@app.route('/')
def index():
    return render_template('index.html',current_time = datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500