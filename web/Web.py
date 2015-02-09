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
from sets import Set

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

    # 格式化 app 信息, 默认取第一个app
    def format_app(app_ip_result):
        audit_app = request.query.audit_app

        if len(app_ip_result) > 0:
            if len(audit_app) <= 0:
                result["audit_app"] = app_ip_result[0]["audit_app"]
            else:
                result["audit_app"] = audit_app
        return

    # 格式化 app 信息, 默认取第一个app
    def format_ip(app_ip_result, app_name):
        audit_ip = request.query.audit_ip

        if len(app_ip_result) > 0:
            if len(audit_ip) <= 0:
                for audit_app_tp in app_ip_result:
                    if audit_app_tp["audit_app"] == app_name:
                        result['audit_ip'] = audit_app_tp['audit_ip']
                        break;
            else:
                result['audit_ip'] = audit_ip
        return

    dbPersisted = DbPersisted()

    # model
    result={}

    # 左面应用名称
    apps = dbPersisted.query_operation(op_mode='query_all_apps')()

    result["left"] = Set(map(lambda x:x['audit_app'], apps))
    format_app(apps)
    result["ips"] = filter(lambda x: x['audit_app'] == result['audit_app'], apps)
    format_ip(apps, result["audit_app"])

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
        result["rows"] = dbPersisted.query_operation(result["audit_ip"], result["audit_app"], result['low_times'], "query_real_data_page")(time_result["start_time"], time_result["end_time"], page_result["offset"], PAGE_SIZE, orderType)

        #记录数量
        result["rowcount"] = dbPersisted.query_operation(result["audit_ip"], result["audit_app"], result['low_times'], "query_real_data_count")(time_result["start_time"], time_result["end_time"])

        result["maxpage"] = result["rowcount"] / PAGE_SIZE + 1

        return template("ta_real", viewmodel = result)
    else:
        result['timeType'] = '0'
        # 记录集合
        result["rows"] = dbPersisted.query_operation(result["audit_ip"], result["audit_app"], result['low_times'], "query_finger_data_page")(time_result["data_time"], page_result["offset"], PAGE_SIZE, orderType)

        #记录数量
        result["rowcount"] = dbPersisted.query_operation(result["audit_ip"], result["audit_app"], result['low_times'], "query_finger_count")(time_result["data_time"])

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
        result['rows'] = dbPersisted.query_operation(op_mode="query_transaction_real_data", low_times = low_times)(finger_print)
        return template("subitem_real", viewmodle = result)
    else:
        result['rows'] = dbPersisted.query_operation(op_mode="query_transaction_data", low_times = low_times)(layer_no, parent_order_nos, finger_print, data_time)
        return template("subitem", viewmodle = result)

# 获取下一级内容,以甘特的样子展现
@route("/gantt")
def getSubItemsGantt():

    # 显示的空白行列数
    show_cloumns = 7
    total_bar_width = 1200 # 满格宽度为1200px

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
    parent_audit_item = dbPersisted.query_operation(op_mode='query_transaction_real_data_by_id', low_times=low_times)(parent_audit_id)

    #原始的最长时间
    org_parent_time_show = int(parent_audit_item['durable_time'])
    # 显示的最长时间设定为花费时间的1.25倍
    parent_time_show = int((org_parent_time_show + show_cloumns - org_parent_time_show % show_cloumns) * 5 / 4)

    # # 组装表头数据, 满页为7列（页面上显示的是约6.3列）
    time_split = int(parent_time_show/(show_cloumns-2))#让最长时间的进度条占满前5列
    result['tr_items'] = map(lambda x:{'tr_no':x, 'tr_time':(x-1)*time_split}, xrange(1,8))

    # 函数调用的入口方法名称
    result['parent_url'] = parent_audit_item['url']

    # 函数调用入口的起始时间
    p_begin_time = long(parent_audit_item['begin_time'])

    # 组装表内容数据
    result['sub_items'] = map(
        lambda item: {'left':(long(item['begin_time']) - p_begin_time) * total_bar_width / parent_time_show,
                      'middle':int((long(item['end_time']) - long(item['begin_time'])) * 1200 / parent_time_show),
                      'url':item['url'].replace('java.lang.', ''),
                      'd_time':int(long(item['begin_time']) - p_begin_time),
                      'c_time':int(long(item['end_time']) - long(item['begin_time']))
        }, dbPersisted.query_operation(op_mode='query_transaction_real_data', low_times = low_times)(parent_audit_id))

    return template("gantt", viewmodel = result)

# 获取下一级内容,以甘特的样子展现
@route("/vm")
def showVMStatus():

    # 传入的时间有两种，一种是单个时间，格式是%Y-%m-%d; 另一种是两个时间，格式是%Y-%m-%d %H:%M:%S
    def format_date():
        # 查询模式, 1, 表示查询明细， 0, 表示概览
        timeType = request.query.timeType
        if not timeType:
            timeType = 0

        # 概揽开始时间
        data_time = request.query.data_time
        # 详请开始时间
        start_time = request.query.start_time
        # 详情结束时间
        end_time = request.query.end_time

        start_time = int(start_time if start_time else time.time())
        end_time = int(end_time if end_time else time.time())
        data_time = int(data_time if data_time else time.time())
            
        start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H")
        end_time_str = datetime.datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H")
        data_time_str = datetime.datetime.fromtimestamp(data_time).strftime("%Y-%m-%d")

        return {"start_time": start_time, "s_time": start_time_str, "end_time": end_time, "e_time": end_time_str, "data_time": data_time, "d_time":data_time_str, "time_type":timeType}
    
    dbPersisted = DbPersisted()
    apps = dbPersisted.query_operation(op_mode='query_all_apps')()
    app = request.query.app
    ip = request.query.ip
    
    # model
    result={}

    if app:
        result['app'] = app
        ls = filter(lambda k : k['audit_app'] == app, apps)
        result['ip'] = ip if ip else (ls[0]['audit_ip'] if ls else (apps[0]['audit_ip'] if apps else 'N/A'))
    else:
        result["app"] = apps[0]['audit_app'] if apps else 'N/A'
        result["ip"] = ip if ip else (apps[0]['audit_ip'] if apps else 'N/A')

    # 左面应用名称
    result["left"] = Set(map(lambda a:a['audit_app'], apps))
    result["apps"] = filter(lambda x:x['audit_app'] == result['app'], apps)
        
    # start end time
    time_result = format_date()
    result["data_time"] = time_result["d_time"]
    result["start_time"] = time_result["s_time"]
    result["end_time"] = time_result["e_time"]
    result['timeType'] = time_result["time_type"]
    
    return template("vm", viewmodel = result)


query_types=[('day', map(lambda x:str(x), range(0, 24))), ('hour',  map(lambda x:str(x), range(0, 60)))]

# retrieving jvm status information in asynchronized way
@route("/vm/status", method='POST')
def getVMStatus():
    
    ip=request.query.ip
    app=request.query.app
    type=int(request.forms.timeType) if request.forms.timeType else 0
    
    watch_time=request.forms.data_time if request.forms.timeType == 0 else request.forms.start_time
    if not watch_time:
        watch_time = time.time()
    
    watch_time = int(watch_time)
    dbPersisted = HeartBeatPgPersisted()
        
    query_operator = dbPersisted.query_operation(watch_time, ip, app, query_types[type][0])
    
    # extract only info_value, info_time fields from a target lst 
    extractor = lambda lst: map(lambda a: {'info_value': a['info_value'], 'info_time': a['info_time']}, lst)
    
    # I don't know how to explain this... okay, the main purpose is to expand a lst2 to length(lst) 
    # e.g. [{'i_t':3, 'i_v': 5}, {'i_t':4, 'i_v': 7}, {'i_t':6, 'i_v': 12}] :=> [{{'i_t':0, 'i_v': 0}}, ..., {'i_t':3, 'i_v': 5}, {'i_t':4, 'i_v': 7}, {'i_t':5, 'i_v': 0} {'i_t':6, 'i_v': 12}, ..., {'i_t':len(lst), 'i_v': 0}]
    expander=(lambda lst: lambda lst2 : map(lambda x: filter(lambda z: z['info_time'] == x, lst2)[0]['info_value'] if x in map(lambda y: y['info_time'], lst2) else 0, lst))(range(0,24) if type == 0 else range(0, 60))
    
    # calculate diff between two nearby value
    # e.g. [{{'i_t':0, 'i_v': 0}}, ..., {'i_t':3, 'i_v': 5}, {'i_t':4, 'i_v': 7}, {'i_t':5, 'i_v': 0} {'i_t':6, 'i_v': 12}, ..., {'i_t':len(lst), 'i_v': 0}] 
    #  :=> [{{'i_t':0, 'i_v': 0}}, ..., {'i_t':3, 'i_v': 5}, {'i_t':4, 'i_v': 2}, {'i_t':5, 'i_v': 0} {'i_t':6, 'i_v':  5}, ..., {'i_t':len(lst), 'i_v': 0}]
    compactor=lambda lst: reduce(lambda s,a: (s[0], s[1] + [a - reduce(lambda s2, a2: a2 + s2, s[1], s[0]) if a != 0 else 0]), lst[1:], (lst[0], [0]))[1]
    
    json_transformer = lambda lst: map(lambda (item_info, item_list): {'seriesData':item_info[3](compactor, expander(extractor(item_list))), 'yMax_value': item_info[4](item_list), 'title':item_info[0], "yAxis_text":item_info[1], "subtitle":item_info[2](item_list[0]) if item_list else '', 'seriesName': item_info[0], 'categories' : query_types[type][1]}, lst)

    # ITEM:-> ITEM_LIST mapping
    status =  map(lambda item: (dbPersisted.TYPE_NAME[item], query_operator(item)), dbPersisted.TYPE_NAME.keys())
    return template(json.dumps({'status':0, 'msg':'', 'data':json_transformer(status)}))
    

if __name__ == '__main__':
    logging.config.fileConfig(LOG_CONFIG)
    run(host=HTTP_HOST, port=HTTP_PORT, reloader=True)
    
    
    