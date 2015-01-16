# !/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:web.py

__author__ = 'yuyichuan'


from dbPersisted import DbPersisted
from bottle import route, run, template, request, redirect, static_file, get, post
import logging
import logging.config
import configCur
import datetime
import time

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
    rows = dbPersisted.query_operation('query_app')()
    return template('left', viewmodel = rows)

# 分页查询
@route('/content')
def content():
    page = request.query.page

    data_time = request.query.qtime
 # 认为是字符串格式的
    if len(data_time) >= 8:
        try:
            t_date_time = int(time.mktime(time.strptime(data_time, "%Y%m%d")))
        except Exception, e:
            # 异常则当作秒来使用
            t_date_time = data_time
    else:
        t_date_time = int(time.time())
    dt_str = datetime.datetime.fromtimestamp(t_date_time).strftime("%Y%m%d")

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
    apps = dbPersisted.query_operation("query_app")()
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
    ips =  dbPersisted.query_operation("query_ip")(app)
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
    result["rows"] = dbPersisted.query_operation("query_finger_data")(dt_str, ip, app, offset, configCur.PAGE_SIZE, True)

    #记录数量
    result["rowcount"] = dbPersisted.query_operation("query_data_count")(dt_str, ip, app)

    # 页码
    result["curpage"] = page
    result["maxpage"] = result["rowcount"] / configCur.PAGE_SIZE + 1
    result["prepage"] = page - 1 if page > 1 else 1
    result["afterpage"] = page + 1
    result["app_en"] = app
    result["ip_en"] = ip
    result["data_time"] = dt_str

    return template("content", viewmodel = result)

# 获取下一级内容
@route("/subitems")
def getItem():
    # 为显示控制样式缩进用的层级标识
    nodeIndex = request.query.nodeIndex
    if len(nodeIndex) == 0 or nodeIndex < 0:
        nodeIndex = 0
    else:
        nodeIndex = int(nodeIndex)

    layer_no = request.query.layerno
    parent_order_nos = request.query.parentordernos
    finger_print = request.query.fingerprint
    data_time = request.query.datatime

    dbPersisted = DbPersisted()

    result = {}

    result['rows'] = dbPersisted.query_operation("query_transaction_data")(layer_no, parent_order_nos, finger_print, data_time)
    result['finger_print'] = finger_print
    result['node_index'] = nodeIndex
    result['text_indent'] = nodeIndex * 10
    result['b_color'] = configCur.table_colors[nodeIndex%len(configCur.table_colors)]


    return template("subitem", viewmodle = result)

if __name__ == '__main__':
    logging.config.fileConfig(configCur.LOG_CONFIG)
    run(host=configCur.HTTP_HOST, port=configCur.HTTP_PORT, reloader=True)