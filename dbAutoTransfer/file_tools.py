#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from Remote_linux import Linux

def file_trancs(source,tag):
    s=source.split(':')
    t=tag.split(':')
    sourceIp=s[0]
    sourceDir=s[1]
    tagIp=t[0]
    tagDir=t[1]
    pass