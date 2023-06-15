#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: main.py
 @devtool: PyCharm
 @date: 2023/6/15
 @file: process.py
"""
import njust.config as c
import re
import ddddocr
import requests


def jwc_login(uid, pwd):
    res = requests.get(url=c.url_verify, headers=c.headers)
    ocr = ddddocr.DdddOcr(beta=True)
    verify_code = ocr.classification(res.content)
    cookies = res.cookies
    print("验证码:", verify_code, "cookies:", cookies)
    body = {
        "USERNAME": uid,
        "PASSWORD": pwd,
        "RANDOMCODE": verify_code
    }
    res = requests.post(url=c.url_login, cookies=cookies, data=body, headers=c.headers, allow_redirects=False)
    location = res.headers.get('Location')
    if location is None:
        return None
    res.close()
    res = requests.get(url=location, headers=c.headers, allow_redirects=True)
    cookies = res.history[-1].cookies.get_dict()
    res.close()
    return cookies


def course_merge(data: set) -> list[tuple]:
    course_weeks = {}
    for course, weeks in data:
        if course.startswith('<br/>----------------------<br>'):
            course = course.replace('<br/>----------------------<br>', '')
        if course not in course_weeks:
            course_weeks[course] = []
        course_weeks[course].append(weeks)

    result = []
    for course, weeks_list in course_weeks.items():
        min_week = 100
        max_week = 0
        for weeks in weeks_list:
            for week_range in weeks.split(','):
                start, _, end = week_range.partition('-')
                start, end = int(start), int(end or start)
                min_week = min(min_week, start)
                max_week = max(max_week, end)
        result.append((course, f'{min_week}-{max_week}'))

    return result


def jwc_course(uid, pwd):
    # 获取登录的cookies
    cookies = jwc_login(uid, pwd)
    # 若没有cookies则表示登录失败
    if cookies is None:
        return 0
    res = requests.get(url=c.url_course, headers=c.headers, cookies=cookies)
    res.close()
    # -----------------------------------------------------------------------
    # # 此部分用于解析课程表内容
    course_table_pattern = r'<table[^>]*id="dataList"[^>]*>[\s\S]*?</table>'  # 匹配id为dataList的table标签
    course_tr_pattern = r'<tr[^>]*>[\s\S]*?</tr>'  # 匹配tr标签
    course_td_pattern = r'<t[hd][^>]*>[\s\S]*?</t[hd]>'  # 匹配td或th标签

    table_course = re.search(course_table_pattern, res.text)  # 查找table标签
    tr_matches = re.findall(course_tr_pattern, table_course.group(0))  # 查找tr标签

    data_course = []
    for tr_match in tr_matches[1:]:  # 跳过第一行表头
        td_matches = re.findall(course_td_pattern, tr_match)  # 查找td或th标签
        row_data = tuple(re.sub(r'<.*?>', '', td_match) for td_match in td_matches)  # 提取每个单元格的文本数据，并构建为元组
        data_course.append(row_data)  # 将元组添加到数据列表中

    # for index, i in enumerate(data_course):
    #     print(index, i)
    # -----------------------------------------------------------------------
    # 解析课程表上课周次
    # 在html文本中匹配id为kbtable的table标签下所有class为kbcontent1的div标签里的数据
    week_table_pattern = r'<table.*?id="kbtable".*?>(.*?)<\/table>'
    table_week = re.findall(week_table_pattern, res.text, re.S)[0]

    week_tr_pattern = r'<div.*?class="kbcontent1".*?>(.*?)<\/div>'
    week_match = re.findall(week_tr_pattern, table_week, re.S)

    con = "\n".join(week_match)
    # print(con)

    week_td_pattern = r'(.+?)<br/><font title=\'(?<!---).*?\'>(.+?)\(周\)</font>'  # 只匹配周次信息
    week_info = re.findall(week_td_pattern, con)
    week_info = set(week_info)
    data_week = course_merge(week_info)
    # for index, i in enumerate(data_week):
    #     print(index, i)

    # -----------------------------------------------------------------------
    # # 开始合并课程
    data = []  # 用来存储返回数据
    for i in data_course:
        info_course = {}  # 用来存课程数据
        addr = i[7].split(",")[0]
        info_course["num"] = i[1]
        info_course["course"] = i[3]
        info_course["teacher"] = i[4]
        info_course["credit"] = float(i[6])
        info_course["addr"] = addr if addr != "" else None
        info_course["type"] = i[8]
        # 上课时间单独处理
        class_pattern = r'星期(\w+)\((\d+)-(\d+)小节\)'
        class_match = re.findall(class_pattern, i[5])
        info_course["time"] = [[c.days_dict[match[0]], int(match[1]), int(match[2])] for match in class_match]
        for w in data_week:
            if i[3] in w[0]:
                info_course["date"] = [int(x) for x in w[1].split('-')]
        data.append(info_course)
    return data


def jwc_score(uid, pwd):
    # 获取登录的cookies
    cookies = jwc_login(uid, pwd)
    # 若没有cookies则表示登录失败
    if cookies is None:
        return 0
    res = requests.get(url=c.url_score, headers=c.headers, cookies=cookies, data=c.data_score)
    res.close()
    # -----------------------------------------------------------------------
    # 获取table标签中id为"dataList"的内容
    table_match = re.findall('<table id="dataList".*?>(.*?)</table>', res.text, re.S)[0]
    # 获取tr标签中的内容
    tr_list = re.findall('<tr.*?>(.*?)</tr>', table_match, re.S)[1:]
    data_score = []
    for tr in tr_list:
        # 获取td标签中的内容
        td_list = re.findall('<td.*?>(.*?)</td>', tr, re.S)
        # 将每个td中的内容作为元组元素，添加到结果列表中
        data_score.append(tuple(td_list))
    # for index, i in enumerate(data_score):
    #     print(index, i)

    # -----------------------------------------------------------------------
    # # 封装成绩数据
    data = []
    for i in data_score:
        info_score = {"num": int(i[0]),
                      "term": i[1],
                      "cid": i[2],
                      "course": i[3],
                      "score": i[4],
                      "credit": float(i[6]),
                      "type": i[9]
                      }  # 用来存成绩数据
        data.append(info_score)
    return data


if __name__ == '__main__':
    print("========== process.py ==========")
