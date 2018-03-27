#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import configparser

cfg = configparser.ConfigParser()
cfg.read('data.cfg')
data = cfg['dz']
print(cfg['dz']['con_name'])
print(data['directory_dir'])