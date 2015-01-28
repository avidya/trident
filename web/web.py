# !/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:web.py

__author__ = 'yuyichuan'


from transactionPersisted import DbPersisted
from bottle import route, run, template, request, redirect, static_file, get, post
import logging
import logging.config
import configCur
import datetime
import time

@route('/hello')
def hello():
    return "Hello World!"

@route('/bar_tp/<filename:path>')
def send_file(filename):
    return static_file(filename, root=configCur.BAR_PATH)

@route('/static/<filename:path>')
def send_file(filename):
    return static_file(filename, root='./static')

# 分页查询
@route('/')
@route('/ta')
def content():

    # 传入的时间有两种，一种是单个时间，格式是%Y-%m-%d; 另一种是两个时间，格式是%Y-%m-%d %H:%M:%S
    def format_date():
        # 查询模式, 1, 表示查询明细， 0, 表示该蓝
        timeType = request.query.timeType

        # 概揽开始时间
        data_time = request.query.data_time
        # 详请开始时间
        start_time = request.query.start_time
        # 详情结束时间
        end_time = request.query.end_time

        if len(start_time) > 8:
            start_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")))
        else:
            start_time = int(time.time())
        start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")

        if len(end_time) > 8:
            end_time = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))
        else:
            end_time = int(time.time())
        end_time_str = datetime.datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")

        if len(data_time) > 8:
            data_time = int(time.mktime(time.strptime(data_time, "%Y-%m-%d")))
        else:
            data_time = int(time.time())

        data_time_str = datetime.datetime.fromtimestamp(data_time).strftime("%Y-%m-%d")

        return {"start_time": start_time, "s_time": start_time_str, "end_time": end_time, "e_time": end_time_str, "data_time": data_time, "d_time":data_time_str, "time_type":timeType}

    # 格式化分页信息
    def format_page():
        page = request.query.page

        if len(page) == 0 or page <= 0:
            page = 1
        else:
            page = int(page)
        offset = (page -1) * configCur.PAGE_SIZE

        return {"page":page, "offset":offset}

    # 格式化ip信息
    def format_ip(app):
        ip = request.query.ip
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
        return {"ip": ip, "ip_address": ip_address, "ips": ips}

    # 格式化 app 信息, 默认取第一个app
    def format_app():
        apps = dbPersisted.query_operation("query_app")()
        app = request.query.app
        app_name = "None"
        if len(apps) > 0:
            if len(app) <= 0:
                app = apps[0]["audit_app_encode"]

            # app name
            for app_tp in apps:
                if app_tp["audit_app_encode"] == app:
                    app_name = app_tp["audit_app"]
                    break
        return {"apps": apps, "app": app, "app_name": app_name}

    dbPersisted = DbPersisted()
    # model
    result={}

    # 左面应用名称
    app_result = format_app()
    result["left"] = app_result["apps"]
    result["app_name"] = app_result["app_name"]
    result["app_en"] = app_result["app"]

    # ip address for human
    ip_result = format_ip(app_result["app"])
    result["ips"] = ip_result["ips"]
    result["ip_address"] = ip_result["ip_address"]
    result["ip_en"] = ip_result["ip"]

    # page info
    page_result = format_page()
    result["curpage"] = page_result["page"]
    result["prepage"] = page_result["page"] - 1 if page_result["page"] > 1 else 1
    result["afterpage"] = page_result["page"] + 1

    # start end time
    time_result = format_date()
    result["data_time"] = time_result["d_time"]
    result["start_time"] = time_result["s_time"]
    result["end_time"] = time_result["e_time"]


    orderType = request.query.orderType
    if orderType == '0':
        orderType = False
    else:
        orderType = True


    if(time_result["time_type"] == '1'): # 查询明细
        # 记录集合
        result["rows"] = dbPersisted.query_operation("query_real_data_page")(time_result["start_time"], time_result["end_time"], ip_result["ip"], app_result["app"], page_result["offset"], configCur.PAGE_SIZE, orderType)

        #记录数量
        result["rowcount"] = dbPersisted.query_operation("query_real_data_count")(time_result["start_time"], time_result["end_time"], ip_result["ip"], app_result["app"])

        result["maxpage"] = result["rowcount"] / configCur.PAGE_SIZE + 1

        return template("ta_real", viewmodel = result)
    else:
        # 记录集合
        result["rows"] = dbPersisted.query_operation("query_finger_data")(time_result["data_time"], ip_result["ip"], app_result["app"], page_result["offset"], configCur.PAGE_SIZE, orderType)

        #记录数量
        result["rowcount"] = dbPersisted.query_operation("query_data_count")(time_result["data_time"], ip_result["ip"], app_result["app"])

        result["maxpage"] = result["rowcount"] / configCur.PAGE_SIZE + 1

        return template("ta", viewmodel = result)

# 获取下一级内容
@route("/subitems")
def getItem():
    # 查询模式, 1, 表示查询明细， 0, 表示该蓝
    timeType = request.query.timeType

    # 为显示控制样式缩进用的层级标识
    nodeIndex = request.query.nodeIndex
    if len(nodeIndex) == 0 or nodeIndex < 0:
        nodeIndex = 0
    else:
        nodeIndex = int(nodeIndex)

    layer_no = request.query.layerno
    parent_order_nos = request.query.parentordernos
    finger_print = request.query.fingerprint
    data_time = request.query.data_time

    dbPersisted = DbPersisted()

    result = {}

    result['finger_print'] = finger_print
    result['node_index'] = nodeIndex
    result['text_indent'] = nodeIndex * 10
    result['b_color'] = configCur.table_colors[nodeIndex%len(configCur.table_colors)]

    if timeType == '1':
        result['rows'] = dbPersisted.query_operation("query_transaction_real_data")(finger_print)
        return template("subitem_real", viewmodle = result)
    else:
        result['rows'] = dbPersisted.query_operation("query_transaction_data")(layer_no, parent_order_nos, finger_print, data_time)
        return template("subitem", viewmodle = result)

if __name__ == '__main__':
    logging.config.fileConfig(configCur.LOG_CONFIG)
    run(host=configCur.HTTP_HOST, port=configCur.HTTP_PORT, reloader=True)