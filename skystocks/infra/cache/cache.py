#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import os
import redis
from os.path import join
from os import environ as ENV
STAGE = ENV.get('stage', 'dev')
_base_dir = os.path.dirname(os.path.abspath(__file__))
default_name = 'cache-dev.yaml'
if STAGE == 'prod':
    config_name = 'cache.yaml'
else:
    config_name = default_name
_cache = join(_base_dir, config_name)
caches = {}
with open(_cache, 'r') as yml_file:
    cache_configs = yaml.safe_load(yml_file)
    for config in cache_configs:
        alias = config['alias']
        host = config['host']
        passwd = config.get('pass', None)
        port = config['port']
        r = redis.Redis(host=host, port=port, db=0, password=passwd)
        caches[alias] = r
