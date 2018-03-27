#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import unittest

from oracle_handle import oracle_handle as oracle
import oracle12c_tools as oratools

class TestDict(unittest.TestCase):


    # 远程数据库导出测试 content='METADATA_ONLY'

    def test_oracle_trancs(self):
        oraclesource=oracle('192.168.30.132','system', 'alpha', 'DZ', 'dianshang315', 'backup')
        oracledes=oracle('192.168.20.160','system', 'alpha', 'dzs1', 'dianshang315', 'backup')

        #oratools.drop_user(oracledes)
        #oratools.oracle_trancs(oraclesource,oracledes)
        oratools.alter_user(oracledes)


if __name__ == '__main__':
    unittest.test_yransport()