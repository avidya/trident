# !/usr/bin/python
# -*- coding: UTF-8 -*-

# Filename:heartbeatPersisted.py

#{
#   "timestamp":1421817696000,
#   "app":"his-web",
#   "gcinfo":[
#               {"count":162,"name":"PS Scavenge","time":5593},
#               {"count":0,"name":"PS MarkSweep","time":0}
#           ],
#   "hostname":"puma",
#   "ip":"10.1.26.20",
#   "memory":{"maxHeap":1431830528,"maxNonHeap":318767104,"usedHeap":528956056,"usedNonHeap":73881336},
#   "thread":{"active":58,"daemon":34,"http":8,"peek":65}
# }

# CREATE TABLE trident_heartbeat_audit
# (
#   audit_id serial NOT NULL,
#   info_time_stamp bigint NOT NULL, -- 消息采集时间， 精确到秒
#   info_type smallint NOT NULL, -- YONGC， OLDGC， HEAP， NOHEAP， THREAD
#   info_name character varying (30) NOT NULL,
#   info_value bigint NOT NULL, --记录项值
#   info_second_value_name character varying(30), --第二项值名称
#   info_second_value bigint, --第二项值
#   ip character varying(100) NOT NULL,
#   app character varying(100) NOT NULL,
#   ip_encode character varying(40) NOT NULL,
#   app_encode character varying(40) NOT NULL,
#   remark character varying(100),
#   create_time timestamp with time zone NOT NULL DEFAULT now(),
#   CONSTRAINT pk_trident_heartbeat_audit PRIMARY KEY (audit_id)
# );
# CREATE INDEX i_heartbeat_audit_ip_app_encode
#    ON trident_heartbeat_audit
#    USING btree
#    (ip_encode, app_encode);
#
#
#
# CREATE TABLE trident_heartbeat_audit_hour
# (
#   audit_id serial NOT NULL,
#   info_time_stamp bigint NOT NULL, -- 消息采集时间, 精确到分钟
#   info_type smallint NOT NULL, -- YONGC， OLDGC， HEAP， NOHEAP， THREAD
#   info_name character varying (30) NOT NULL,
#   info_value bigint NOT NULL, --记录项值
#   info_second_value_name character varying(30), --第二项值名称
#   info_second_value bigint, --第二项值
#   ip character varying(100) NOT NULL,
#   app character varying(100) NOT NULL,
#   ip_encode character varying(40) NOT NULL,
#   app_encode character varying(40) NOT NULL,
#   times integer NOT NULL DEFAULT 1, --记录的次数
#   remark character varying(100),
#   create_time timestamp with time zone NOT NULL DEFAULT now(),
#   CONSTRAINT pk_trident_heartbeat_hour_audit PRIMARY KEY (audit_id)
# );
#
# CREATE INDEX i_trident_heartbeat_audit_hour_ip_app_encode
#    ON trident_heartbeat_audit_hour
#    USING btree
#    (ip_encode, app_encode);
#
#
#
# CREATE TABLE trident_heartbeat_audit_day
# (
#   audit_id serial NOT NULL,
#   info_time_stamp bigint NOT NULL, -- 消息采集时间，精确到小时
#   info_type smallint NOT NULL, -- YONGC， OLDGC， HEAP， NOHEAP， THREAD
#   info_name character varying (30) NOT NULL,
#   info_value bigint NOT NULL, --记录项值
#   info_second_value_name character varying(30), --第二项值名称
#   info_second_value bigint, --第二项值
#   ip character varying(100) NOT NULL,
#   app character varying(100) NOT NULL,
#   ip_encode character varying(40) NOT NULL,
#   app_encode character varying(40) NOT NULL,
#   times integer NOT NULL DEFAULT 1, --记录的次数
#   remark character varying(100),
#   create_time timestamp with time zone NOT NULL DEFAULT now(),
#   CONSTRAINT pk_trident_heartbeat_day_audit PRIMARY KEY (audit_id)
# );
# CREATE INDEX i_trident_heartbeat_audit_day_ip_app_encode
#    ON trident_heartbeat_audit_day
#    USING btree
#    (ip_encode, app_encode);
#


__author__ = 'yuyichuan'

import pg
import json
import logging
import logging.config
from Config import *
import hashlib
import datetime
import time
import infoBargraphs

class HeartBeatPgPersisted:

    YOUNG_GC = 1
    OLD_GC = 2
    HEAP = 3
    NON_HEAP = 4
    THREAD_ACTIVE = 5
    THREAD_DAEMON = 6
    THREAD_HTTP = 7

    TYPE_NAME = {
        YOUNG_GC: "yong gc",
        OLD_GC:"old gc",
        HEAP:"heap memory",
        NON_HEAP:"noHeap memory",
        THREAD_ACTIVE:" active thread",
        THREAD_DAEMON:"daemon thread",
        THREAD_HTTP:"http thread"
    }

    # 获取 logger
    def get_log(self):
        return logging.getLogger("PgPersisted")

    # 保存接收到的消息数据
    def save_heart_beat_info_json(self, data_str):

        # 保存ip，允许失败
        def saveHostIp(ip, app, hostName):
            try:
                hashapp_tp = hashlib.md5()
                hashapp_tp.update(app)

                haship_tp = hashlib.md5()
                haship_tp.update(ip)

                if db.query("select count(audit_ip) from trident_audit_ip where audit_ip_encode ='%s' and audit_app_encode='%s' " % (haship_tp.hexdigest(), hashapp_tp.hexdigest())).getresult()[0][0] == 0:
                    db.query("insert into trident_audit_ip(audit_ip, audit_ip_encode, audit_app_encode, host_name) values('%s', '%s', '%s', '%s')" % (ip, haship_tp.hexdigest(), hashapp_tp.hexdigest(), hostName))
            except Exception, e:
                self.get_log().warn("save audit_ip failed, ret=%s" % e.args[0])
            return

        # 保存app， 允许失败
        def saveHostApp(app):
            try:
                hashapp_tp = hashlib.md5()
                hashapp_tp.update(app)

                if db.query("select count(audit_app) from trident_audit_app where audit_app_encode ='%s'" % hashapp_tp.hexdigest()).getresult()[0][0] == 0:
                    db.query("insert into trident_audit_app(audit_app, audit_app_encode) values('%s', '%s')" % (app, hashapp_tp.hexdigest()))
            except Exception, e:
                self.get_log().warn("save audit_app failed, ret=%s" % e.args[0])
            return

        # 保存心跳消息数据, 精确到秒
        def save_trident_heartbeat_audit(da):
            db.query(sql_insert_format % ('trident_heartbeat_audit', int(da[0]/1000), da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10]))
            return

        # 保存心跳消息数据， 精确到分钟
        def save_trident_heartbeat_audit_hour(da):

            dd_time = datetime.datetime(*(time.localtime(int(da[0]/1000)))[:5])
            i_et = int(time.mktime(dd_time.timetuple()))



            if db.query(sql_count_format % ('trident_heartbeat_audit_hour', da[8], da[9], i_et, da[1])).getresult()[0][0] == 0:
                db.query(sql_insert_format % ('trident_heartbeat_audit_hour', i_et, da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10]))
            else:
                db.query(sql_update_format % ('trident_heartbeat_audit_hour', da[3], i_et, da[8], da[9], da[1]))
            return

        # 保存心跳消息数据， 精确到小时
        def save_trident_heartbeat_audit_day(da):
            dd_time = datetime.datetime(*(time.localtime(int(da[0]/1000)))[:4])
            i_et = int(time.mktime(dd_time.timetuple()))

            if db.query(sql_count_format % ('trident_heartbeat_audit_day', da[8], da[9], i_et, da[1])).getresult()[0][0] == 0:
                db.query(sql_insert_format % ('trident_heartbeat_audit_day', i_et, da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10]))
            else:
                db.query(sql_update_format % ('trident_heartbeat_audit_day', da[3], i_et, da[8], da[9], da[1]))
            return

        # 保存一项心跳数据
        def save_heart_beat_info_item(da):
            save_trident_heartbeat_audit(da)
            save_trident_heartbeat_audit_hour(da)
            save_trident_heartbeat_audit_day(da)
            return

        self.get_log().info(data_str)

        data_json = json.loads(data_str, "utf-8")

        # to connect db
        try:
            db = pg.connect(DB_NAME, DB_HOST, DB_PORT, None, None, DB_USER, DB_PWD)
        except Exception, e:
            # print e.args[0]
            self.get_log().error("to connect db failed, ret=%s" % e.args[0])
            return

        saveHostIp(data_json["ip"], data_json["app"], data_json["hostname"])
        saveHostApp(data_json["app"])


        sql_insert_format = "insert into %s (info_time_stamp, info_type, info_name, info_value, info_second_value_name, info_second_value, ip, app, ip_encode, app_encode, remark) " \
                            "values(%s, %s, '%s', %s, '%s', %s, '%s', '%s', '%s', '%s', '%s')"
        sql_update_format = "update %s set info_value = (times * info_value + %s)/(times + 1), times = times + 1 where info_time_stamp = %s and ip_encode = '%s' and app_encode = '%s' and info_type = %s "

        sql_count_format = "select count(*) from %s where ip_encode ='%s' and app_encode='%s' and info_time_stamp =%s and info_type=%s "

        hashapp_tp = hashlib.md5()
        hashapp_tp.update(data_json["app"])
        hashapp_tp_str = hashapp_tp.hexdigest()

        haship_tp = hashlib.md5()
        haship_tp.update(data_json["ip"])
        haship_tp_str = haship_tp.hexdigest()

        # memory_heap save
        save_heart_beat_info_item([data_json["timestamp"], self.HEAP, "heapMemory", int(data_json["memory"]["usedHeap"]/(1024*1024)), "maxHeap",  int(data_json["memory"]["maxHeap"]/(1024*1024)), data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, ''])

        # memory_non_heap save
        save_heart_beat_info_item([data_json["timestamp"], self.NON_HEAP, "nonHeapMemory", int(data_json["memory"]["usedNonHeap"]/(1024*1024)), "maxNonHeap",  int(data_json["memory"]["maxNonHeap"]/(1024*1024)), data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, ''])

        # young gc save
        save_heart_beat_info_item([data_json["timestamp"], self.YOUNG_GC, "count", data_json["gcinfo"][0]["count"], "time",  data_json["gcinfo"][0]["time"], data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, data_json["gcinfo"][0]["name"]])

        # old gc save
        save_heart_beat_info_item([data_json["timestamp"], self.OLD_GC, "count", data_json["gcinfo"][1]["count"], "time",  data_json["gcinfo"][1]["time"], data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, data_json["gcinfo"][1]["name"]])

        # thread save
        save_heart_beat_info_item([data_json["timestamp"], self.THREAD_ACTIVE, "active", data_json["thread"]["active"], "peek", data_json["thread"]["peek"], data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, ''])
        save_heart_beat_info_item([data_json["timestamp"], self.THREAD_DAEMON, "daemon", data_json["thread"]["daemon"], "peek", data_json["thread"]["peek"], data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, ''])
        save_heart_beat_info_item([data_json["timestamp"], self.THREAD_HTTP, "http", data_json["thread"]["http"], "peek", data_json["thread"]["peek"], data_json["ip"], data_json["app"], haship_tp_str, hashapp_tp_str, ''])

    # db 查询操作
    def query_operation(self, op_mode="minute"):

        # 时间轴单位为秒
        unit_second = 1
        # 时间轴单位为分
        unit_minute = 2
        # 时间轴单位为小时
        unit_hour = 3

        def query_data(end_time, ip_encode, app_encode, info_type, unit_type):

            # 格式化返回数据
            def format_result(db_result, file_name):
                retDict = {"file_name": file_name}

                data_list = []
                rows = db_result.getresult()
                for row in rows:
                    item = {}
                    info_time = datetime.datetime(*(time.localtime(row[0]))[:6])
                    if unit_type == unit_second:
                        info_time_x = "%sS" % info_time.timetuple().tm_sec
                    elif unit_type == unit_minute:
                        info_time_x = "%sM" % info_time.timetuple().tm_min
                    elif unit_type == unit_hour:
                        info_time_x = "%sH" % info_time.timetuple().tm_hour

                    item['info_time'] = info_time_x
                    item['info_type'] = row[1]
                    item['info_name'] = row[2]
                    item['info_value'] = int(row[3])
                    item['info_second_value_name'] = row[4]
                    item['info_second_value'] = row[5]
                    item['remark'] = row[6]
                    data_list.append(item)

                retDict["data_list"] = data_list
                return retDict

            # 生产文件名称: 以 ip, app, info_type, start_time, end_time, unit_type 来生产文件名
            def create_file_name(start_time, end_time):
                hash_file_name = hashlib.md5()
                hash_file_name.update("dry_%s" % unit_type)
                hash_file_name.update("ayz_%s" % info_type)
                hash_file_name.update(ip_encode)
                hash_file_name.update(app_encode)
                hash_file_name.update("%s" % start_time)
                hash_file_name.update("%s" % end_time)


                return "%s" % hash_file_name.hexdigest()

            time_t = time.localtime(end_time)
            if unit_type == unit_second:
                 dd_time = datetime.datetime(*(time_t)[:5])
                 start_time = int(time.mktime(dd_time.timetuple()))
                 end_time = start_time + 60
                 table_name = "trident_heartbeat_audit"
            elif unit_type == unit_minute:
                 dd_time = datetime.datetime(*(time_t)[:4])
                 start_time = int(time.mktime(dd_time.timetuple()))
                 end_time = start_time + 60*60
                 table_name = "trident_heartbeat_audit_hour"
            elif unit_type == unit_hour:
                 dd_time = datetime.datetime(*(time_t)[:3])
                 start_time = int(time.mktime(dd_time.timetuple()))
                 end_time = start_time + 60*60*24
                 table_name = "trident_heartbeat_audit_day"

            sql_select = "select info_time_stamp, info_type, info_name, info_value, info_second_value_name, info_second_value, remark from %s " \
                         "where ip_encode = '%s' and app_encode = '%s' and info_type = %s and info_time_stamp >= %s and info_time_stamp < %s order by info_time_stamp asc"

            sql_select = sql_select % (table_name, ip_encode, app_encode, info_type, start_time, end_time)

            return format_result(db.query(sql_select), create_file_name(start_time, end_time))


        # 时间轴以秒为单位
        def query_minute(end_time, ip_encode, app_encode, info_type):
           # 到秒
           return query_data(end_time, ip_encode, app_encode, info_type, unit_second)

        # 时间轴以分为单位
        def query_hour(end_time, ip_encode, app_encode, info_type):
            # 到小时
            return query_data(end_time, ip_encode, app_encode, info_type, unit_minute)

        # 时间轴以小时为单位
        def query_day(end_time, ip_encode, app_encode, info_type):
            # 到分
            return query_data(end_time, ip_encode, app_encode, info_type, unit_hour)

        db = pg.connect(DB_NAME, DB_HOST, DB_PORT, None, None, DB_USER, DB_PWD)

        ops = {'minute': query_minute, 'hour':query_hour, 'day':query_day}

        return ops[op_mode]

# main
if __name__ == '__main__':

    logging.config.fileConfig(LOG_CONFIG)
    dbPersisted = HeartBeatPgPersisted()
    # insert test
    json_str ='{' \
              '"timestamp":%s,' \
              '"app":"his-web",' \
              '"gcinfo":[{"count":162,"name":"PS Scavenge","time":5593},{"count":0,"name":"PS MarkSweep","time":0}],' \
              '"hostname":"puma",' \
              '"ip":"10.1.26.20",' \
              '"memory":{"maxHeap":1431830528,"maxNonHeap":318767104,"usedHeap":528956056,"usedNonHeap":73881336},' \
              '"thread":{"active":58,"daemon":34,"http":8,"peek":65}' \
              '}'

    # for i in xrange(1,1000):
    #     dbPersisted.save_heart_beat_info_json(json_str % (1421817696321 + (i * 10000)))

    # query test
    try:

        def construct_bar_data(org_data_dict):
            # data_list = []
            # i = 0
            # data_list.append('0     0'+'\n')
            # for item in org_data_dict["data_list"]:
            #     i = i+1
            #     data_list.append('%s' % item["info_value"]+'   ' + '%s:%s' % (i, item['info_time']) + '\n')
            # data_list.append('0     0'+'\n')
            data_list = ['%s' % item["info_value"]+'   ' + '%s' % item['info_time'] + '\n' for item in org_data_dict["data_list"]]
            #if len(data_list) == 1:
            data_list.append('0     s'+'\n')

            return data_list

        bar = infoBargraphs.Bargraphs()

        second_result = dbPersisted.query_operation()(1421817696, "281af57697156df10bc3f28458dad80f", "752a64b61ddb026c45e1158b4cd2d453", dbPersisted.THREAD_ACTIVE)
        bar.create_bar_png(construct_bar_data(second_result), second_result["file_name"], None, None, True)

        minute_result = dbPersisted.query_operation("hour")(1421817696, "281af57697156df10bc3f28458dad80f", "752a64b61ddb026c45e1158b4cd2d453", dbPersisted.NON_HEAP)
        bar.create_bar_png(construct_bar_data(minute_result), minute_result["file_name"], None, None, True)

        hour_result = dbPersisted.query_operation("day")(1421817696, "281af57697156df10bc3f28458dad80f", "752a64b61ddb026c45e1158b4cd2d453", dbPersisted.YOUNG_GC)
        bar.create_bar_png(construct_bar_data(hour_result), hour_result["file_name"], None, None, True)

    except Exception, e:
        dbPersisted.get_log().error("operation failed, ret=%s" % e.args[0])


# End of heartbeatPersisted.py