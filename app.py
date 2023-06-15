#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: main.py
 @devtool: PyCharm
 @date: 2023/6/15
 @file: app.py
"""
import njust
from njust import *
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/course', methods=['POST'])
def course():
    # 获取POST请求参数
    uid = request.json.get('uid')
    pwd = request.json.get('pwd')

    # TODO: 对学号和密码进行验证

    # 登录到教务系统，获取课程信息
    # TODO: 调用登录方法，获取课程信息

    # 处理获取到的课程信息，组成API返回内容
    data = process.jwc_course(uid=uid, pwd=pwd)
    code = 200
    if data == 0:
        data = None
        code = 401
    # 组成API返回内容
    ret = {
        "code": code,
        "data": data
    }

    return jsonify(ret)


@app.route('/score', methods=['POST'])
def score():
    # 获取POST请求参数
    uid = request.json.get('uid')
    pwd = request.json.get('pwd')

    # TODO: 对学号和密码进行验证

    # 登录到教务系统，获取成绩信息
    # TODO: 调用登录方法，获取成绩信息

    # 处理获取到的课程信息，组成API返回内容
    data = process.jwc_score(uid=uid, pwd=pwd)
    code = 200
    if data == 0:
        data = None
        code = 401
    # 组成API返回内容
    ret = {
        "code": code,
        "data": data
    }

    return jsonify(ret)


if __name__ == '__main__':
    print(njust.__doc__)
    app.run(debug=True, host='0.0.0.0', port=8080)