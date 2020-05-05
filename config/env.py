#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : sikai.zhang
# @Time    : 5/24/19 10:00 AM
from os import environ as ENV, path as PATH

ENV['root'] = PATH.abspath(PATH.join(PATH.dirname(__file__), '..'))
STAGE = ENV.get('stage', 'dev')
