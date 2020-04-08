#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : sikai.zhang
# @Time    : 5/24/19 9:41 AM
# this file must be put in the same dir as database-*.yaml
import os
from collections import defaultdict
from os.path import join
import yaml
from os import environ as ENV
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

STAGE = ENV.get('stage', 'dev')
_base_dir = os.path.dirname(os.path.abspath(__file__))

default_name = 'database-dev.yaml'
if STAGE == 'test':
    config_name = 'database-test.yaml'
elif STAGE == 'prod':
    config_name = 'database.yaml'
else:
    config_name = default_name

_db = join(_base_dir, config_name)
engines = dict()
sessions = dict()
with open(_db, 'r') as yml_file:
    db_configs = yaml.safe_load(yml_file)
    for config in db_configs:
        alias = config['alias']
        engine = create_engine(config['urls'][0], echo=config['echo'])
        Session = sessionmaker(bind=engine)
        sessions[alias] = Session
        engines[alias] = engine

Base = declarative_base()
