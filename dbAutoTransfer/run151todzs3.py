#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import json
from oracle_handle import oracle_handle as oracle
import oracle12c_tools as oratools
import configparser
import json




def trancs(source,des):
    cfg = configparser.ConfigParser()
    cfg.read('data.cfg')
    oraclesource=oracle(cfg[source])
    oracledes=oracle(cfg[des])

    oratools.drop_user(oracledes)
    oratools.oracle_trancs(oraclesource, oracledes)
    oratools.alter_user(oracledes)
    #print(json.dumps(oraclesource, default=lambda obj: obj.__dict__))
    #print(json.dumps(oracledes, default=lambda obj: obj.__dict__))


trancs('dz151','dzs3')