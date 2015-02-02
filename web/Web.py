# !/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:web.py

__author__ = 'yuyichuan'


from transactionPersisted import DbPersisted
from heartbeatPersisted import HeartBeatPgPersisted
from bottle import route, run, template, request, redirect, static_file, get, post
import logging
import logging.config
from Config import *
import datetime
import time
import json

@route('/static/<filename:path>')
def send_file(filename):
    return static_file(filename, root='./static')

@route('/test')
def aaa():
    return template('test')

# 分页查询
@route('/')
@route('/ta')
def content():

    # 传入的时间有两种，一种是单个时间，格式是%Y-%m-%d; 另一种是两个时间，格式是%Y-%m-%d %H:%M:%S
    def format_date():
        # 查询模式, 1, 表示查询明细， 0, 表示概览
        timeType = request.query.timeType

        # 概揽开始时间
        data_time = request.query.data_time
        # 详请开始时间
        start_time = request.query.start_time
        # 详情结束时间
        end_time = request.query.end_time

        start_time = int(start_time if start_time else time.time())
        end_time = int(end_time if end_time else time.time())
        data_time = int(data_time if data_time else time.time())
            
        start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = datetime.datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")
        data_time_str = datetime.datetime.fromtimestamp(data_time).strftime("%Y-%m-%d")

        return {"start_time": start_time, "s_time": start_time_str, "end_time": end_time, "e_time": end_time_str, "data_time": data_time, "d_time":data_time_str, "time_type":timeType}

    # 格式化分页信息
    def format_page():
        page = request.query.page

        if len(page) == 0 or page <= 0:
            page = 1
        else:
            page = int(page)
        offset = (page -1) * PAGE_SIZE

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

    #排序类型
    orderType = request.query.orderType
    if orderType == '0':
        orderType = False
        result['order_type'] = '0'
    else:
        orderType = True
        result['order_type'] = '1'

    #时间下限值
    low_times = request.query.low_times
    if low_times is None or len(low_times) == 0:
        low_times = 0
    else:
        try:
            low_times = int(low_times)
        except:
            low_times = 0

    result['low_times'] = low_times

    if(time_result["time_type"] == '1'): # 查询明细
        result['timeType'] = '1'
        # 记录集合
        result["rows"] = dbPersisted.query_operation("query_real_data_page")(time_result["start_time"], time_result["end_time"], ip_result["ip"], app_result["app"], page_result["offset"], PAGE_SIZE, orderType, low_times)

        #记录数量
        result["rowcount"] = dbPersisted.query_operation("query_real_data_count")(time_result["start_time"], time_result["end_time"], ip_result["ip"], app_result["app"], low_times)

        result["maxpage"] = result["rowcount"] / PAGE_SIZE + 1

        return template("ta_real", viewmodel = result)
    else:
        result['timeType'] = '0'
        # 记录集合
        result["rows"] = dbPersisted.query_operation("query_finger_data")(time_result["data_time"], ip_result["ip"], app_result["app"], page_result["offset"], PAGE_SIZE, orderType, low_times)

        #记录数量
        result["rowcount"] = dbPersisted.query_operation("query_data_count")(time_result["data_time"], ip_result["ip"], app_result["app"], low_times)

        result["maxpage"] = result["rowcount"] / PAGE_SIZE + 1

        return template("ta", viewmodel = result)

# 获取下一级内容
@route("/subitems")
def getSubItems():
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

    #时间下限值
    low_times = request.query.low_times
    if low_times is None or len(low_times) == 0:
        low_times = 0
    else:
        try:
            low_times = int(low_times)
        except:
            low_times = 0

    result['low_times'] = low_times
    result['finger_print'] = finger_print
    result['node_index'] = nodeIndex
    result['text_indent'] = nodeIndex * 10
    result['b_color'] = table_colors[nodeIndex%len(table_colors)]

    if timeType == '1':
        result['rows'] = dbPersisted.query_operation("query_transaction_real_data")(finger_print, low_times)
        return template("subitem_real", viewmodle = result)
    else:
        result['rows'] = dbPersisted.query_operation("query_transaction_data")(layer_no, parent_order_nos, finger_print, data_time, low_times)
        return template("subitem", viewmodle = result)

# 获取下一级内容,以甘特的样子展现
@route("/gantt")
def getSubItemsGantt():

    # 显示的空白行列数
    show_cloumns = 7
    total_bar_width = 1200 # 满格宽度为1200px

    # 组装表内容数据
    def format_sub_result(sub_items_result, parent_result, parent_time_show):
        p_begin_time = long(parent_result['begin_time'])

        f_sub_items_result = []
        for item in sub_items_result:
            sub_item = {}
            # 起始位置为（（当前开始时间 - 父节点开始时间 ）* 100 / 父节点总共花费的时间 ） %
            left = (long(item['begin_time']) - p_begin_time) * total_bar_width / parent_time_show
            sub_item['left'] = left
            sub_item['middle'] = int((long(item['end_time']) - long(item['begin_time'])) * 1200 / parent_time_show)
            sub_item['url'] =  item['url'].replace('java.lang.', '')
            sub_item['d_time'] = int(long(item['begin_time']) - p_begin_time)
            sub_item['c_time'] = int(long(item['end_time']) - long(item['begin_time']))
            f_sub_items_result.append(sub_item)

        return f_sub_items_result

    # 组装表头数据
    def format_parent_audit(parent_result, parent_time_show):
        parent_infos = []
        time_split = int(parent_time_show/show_cloumns)
        for i in xrange(1,8):
            p_item = {}
            p_item['tr_no'] = i
            p_item['tr_time'] = (i-1) * time_split
            parent_infos.append(p_item)

        return parent_infos

    # 父亲节点id
    parent_audit_id = request.query.parent_audit_id

    #时间下限值
    low_times = request.query.low_times

    if low_times is None or len(low_times) == 0:
        low_times = 0
    else:
        try:
            low_times = int(low_times)
        except:
            low_times = 0
    result = {}
    dbPersisted = DbPersisted()

    # 父节点记录信息
    parent_audit_item = dbPersisted.query_operation("query_transaction_real_data_by_id")(parent_audit_id)

    parent_time_show = int(parent_audit_item['durable_time'])
    # 最长时间设定为花费时间的1.25倍
    parent_time_show = int((parent_time_show + show_cloumns - parent_time_show % show_cloumns) * 5 / 4)

    result['tr_items'] = format_parent_audit(parent_audit_item, parent_time_show)
    result['parent_url'] = parent_audit_item['url']
    result['sub_items'] = format_sub_result(dbPersisted.query_operation("query_transaction_real_data")(parent_audit_id, low_times), parent_audit_item, parent_time_show)

    return template("gantt", viewmodel = result)

# 获取下一级内容,以甘特的样子展现
@route("/vm")
def showVMStatus():
    # 传入的时间有两种，一种是单个时间，格式是%Y-%m-%d; 另一种是两个时间，格式是%Y-%m-%d %H:%M:%S
    def format_date():
        # 查询模式, 1, 表示查询明细， 0, 表示概览
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
    
    dbPersisted = DbPersisted()
    
    # model
    result={}

    # 左面应用名称
    app_result = format_app()
    result["left"] = app_result["apps"]
    result["app_name"] = app_result["app_name"]
    result["app_en"] = app_result["app"]

    # start end time
    time_result = format_date()
    result["data_time"] = time_result["d_time"]
    result["start_time"] = time_result["s_time"]
    result["end_time"] = time_result["e_time"]

    # ip address for human
    ip_result = format_ip(app_result["app"])
    result["ips"] = ip_result["ips"]
    result["ip_address"] = ip_result["ip_address"]
    result["ip_en"] = ip_result["ip"]
    
    result['timeType'] = 1

    return template("vm", viewmodel = result)


day_list_series = map(lambda x:str(x), range(0, 24))
hour_list_series = map(lambda x:str(x), range(0, 60))
types=[('day', day_list_series), ('hour', hour_list_series)]
# 异步获取虚拟机状态
@route("/vm/status", method='POST')
def getVMStatus():
    ip=request.query.ip
    app=request.query.app
    type=int(request.query.type)
    watch_time=request.query.data_time if request.query.timeType == 0 else request.query.start_time
    if not watch_time:
        watch_time = int(time.time())
    
    dbPersisted = HeartBeatPgPersisted()
        
    query_operator = dbPersisted.query_operation(watch_time, ip, app, types[type][0])
        
    merger = lambda s, a: s + [a['info_value']]
    stuffer=lambda type:lambda l: l + [0] * (len(types[type][1]) - len(l))
    s=stuffer(type)
    
    # calculus. turn [(item1, item_list1), (item2, item_list2), ... (itemN, item_listN)] into JSON format
    json_transformer = lambda (item_info, item_list): {'seriesData' : s(reduce(merger, item_list, [])), 'title' : item_info[0], "yAxis_text" : item_info[1], "subtitle": item_info[2](item_list[0]), 'seriesName': item_info[0], 'categories' : types[type][1]}

    # ITEM:-> ITEM_LIST mapping
    status =  map(lambda item: (dbPersisted.TYPE_NAME[item], query_operator(item)), dbPersisted.TYPE_NAME.keys())
    return template(json.dumps({'status':0, 'msg':'', 'data':map(json_transformer, status)}))
    

if __name__ == '__main__':
    logging.config.fileConfig(LOG_CONFIG)
    run(host=HTTP_HOST, port=HTTP_PORT, reloader=True)