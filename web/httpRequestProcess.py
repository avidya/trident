# !/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:httpRequestProcess.py

__author__ = 'yuyichuan'


from dbPersisted import DbPersisted
from bottle import route, run, template, request, redirect, static_file, get, post
import logging
import logging.config
import configCur

@route('/hello')
def hello():
    return "Hello World!"

@route('/static/<filename:path>')
def send_file(filename):
    return static_file(filename, root='./static')

@route('/')
def index():
    return template('main')

@route('/left')
def left():
    dbPersisted = DbPersisted()
    rows = dbPersisted.queryOperation('query_app')()
    return template('left', viewmodel = rows)

# 分页查询
@route('/content')
def content():
    page = request.query.page
    if len(page) == 0 or page <= 0:
        page = 1
    else:
        page = int(page)

    ip = request.query.ip

    offset = (page -1) * configCur.PAGE_SIZE

    dbPersisted = DbPersisted()

    # model
    result={}
    app = request.query.app

    # 默认取第一个app
    apps = dbPersisted.queryOperation("query_app")()
    if len(apps) == 0:
        return "nothing..."

    if len(app) <= 0:
        app = apps[0]["audit_app_encode"]

    # app name
    for app_tp in apps:
        if app_tp["audit_app_encode"] == app:
            app_name = app_tp["audit_app"]
            break

    result["app_name"] = app_name
    # 默认显示欢迎页面


    # ip 列表,若没有传入，默认取第一个ip
    ips =  dbPersisted.queryOperation("query_ip")(app)
    result["ips"] = ips
    if len(ip) <= 0 :
        ip = ips[0]['audit_ip_encode']
        ip_address = ips[0]["audit_ip"]
    else:
        for ip_tp in ips:
            if ip_tp["audit_ip_encode"] == ip :
                ip_address = ip_tp["audit_ip"]
                break

    # ip address for human
    result["ip_address"] = ip_address

    # 记录集合
    result["rows"] = dbPersisted.queryOperation("query_data")(0, 0, None, offset, configCur.PAGE_SIZE, True, None, None, app if len(app) > 0 else None, ip if len(ip) > 0 else None)
    #记录数量
    result["rowcount"] = dbPersisted.queryOperation("query_data_count")(0, 0, None, None, None, app if len(app) > 0 else None, ip if len(ip) > 0 else None)

    # 页码
    result["curpage"] = page
    result["maxpage"] = result["rowcount"] / configCur.PAGE_SIZE + 1
    result["prepage"] = page - 1 if page > 1 else 1
    result["afterpage"] = page + 1
    result["app_en"] = app
    result["ip_en"] = ip

    return template("content", viewmodel = result)

# 获取下一级内容
@route("/subitems/<parentId>")
def getItem(parentId):
    # 为显示控制样式缩进用的层级标识
    nodeIndex = request.query.nodeIndex
    if len(nodeIndex) == 0 or nodeIndex < 0:
        nodeIndex = 0
    else:
        nodeIndex = int(nodeIndex)

    app = request.query.app
    ip = request.query.ip
    dbPersisted = DbPersisted()

    result = {}
    result['rows'] = dbPersisted.queryOperation("query_data")(0, parentId, None, 0, 999, True, None, None, app if len(app) > 0 else None, ip if len(ip) > 0 else None)
    result['node_index'] = nodeIndex
    result['text_indent'] = nodeIndex * 10
    result['b_color'] = configCur.table_colors[nodeIndex%len(configCur.table_colors)]


    return template("subitem", viewmodle = result)

if __name__ == '__main__':
    logging.config.fileConfig(configCur.LOG_CONFIG)
    run(host=configCur.HTTP_HOST, port=configCur.HTTP_PORT, reloader=True)