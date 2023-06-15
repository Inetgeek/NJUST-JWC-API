#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: main.py
 @devtool: PyCharm
 @date: 2023/6/15
 @file: config.py
"""

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
}

url_verify = "http://202.119.81.112:8080/verifycode.servlet"
url_login = "http://202.119.81.112:8080/Logon.do?method=logon"
url_course = "http://202.119.81.112:9080/njlgdx/xskb/xskb_list.do"
url_score = "http://202.119.81.112:9080/njlgdx/kscj/cjcx_list"

days_dict = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7}
data_score = {
    "xsfs": "max"
}

if __name__ == '__main__':
    print("========== config.py ==========")
