# !/usr/bin/python
# -*- coding: UTF-8 -*-

# Filename:dbPersisted.py

# 以整个调用链的url取一个指纹，并以这个指纹为区分，将相同指纹的调用分组处理，分别计算不同层级的平均调用时间。考虑到同一层的循环调用时url相
# 同，所以再加上一个同层级的序号来定位，如下：
# url
#   |--url-1-0
#   |   |--url-2-0
#   |   |   |
#   |   |   |--url-3-0
#   |   |   |--url-3-1
#   |   .   .
#   |   .   .
#   |   .
#   |   |--url-2-n
#   |   |
#   .
#   .
#   .
#   |--url-1-n
#
# 指纹的计算方式为函数调用链上的各个函数依次处理，再加上对应的应用，以及该应用所在的app

# 将监控消息内容存入关系数据库中，存放的表结构如下：
#
# --drop table trident_audit;
# --消息记录详情表
# CREATE TABLE trident_audit
# (
#   audit_id serial NOT NULL,
#   root_audit_id integer NOT NULL,                 --根节点id
#   parent_audit_id integer NOT NULL,               --父节点id，0表示顶层记录
#   hostname character varying(50) NOT NULL,        --主机名
#   ip character varying(100) NOT NULL,             --ip地址
#   app character varying(100) NOT NULL,            --应用名
#   ip_encode character varying(40) NOT NULL,       --ip地址 md5
#   app_encode character varying(40) NOT NULL,      --应用名 md5
#   async character varying(20) NOT NULL,           --异步或同步调用
#   url character varying(800) NOT NULL,            --函数调用的方法
#   attachments character varying(800),             --函数调用方法时传送的参数
#   begin_time bigint NOT NULL,                     --函数调用开始时间
#   end_time bigint NOT NULL,                       --函数调用结束时间
#   durable_time integer NOT NULL,                  --函数调用所花时长
#   success character varying(6) NOT NULL,          --函数调用成功与否
#   layer_no  integer NOT NULL,                     --在函数调用链上的层次编号
#   order_no  integer NOT NULL,                     --在同一层次上的序号
#   parent_order_nos character varying(500)  NOT NULL,   --上一层次的order，格式为 上层-上层-上层......
#   finger_print character varying(64) NOT NULL DEFAULT ''::character varying,    --改函数调用所在的指纹
#   create_time timestamp with time zone NOT NULL DEFAULT now(),    --信息采集的时间
#   CONSTRAINT pk_trident_audit PRIMARY KEY (audit_id)
# );
#
# CREATE INDEX i_trident_audit_root_audit_id
#   ON trident_audit
#   USING btree
#   (root_audit_id);
#
# CREATE INDEX i_trident_audit_finger_print_layer_order
#   ON trident_audit
#   USING btree
#   (finger_print, layer_no, order_no);
#
#  CREATE INDEX i_trident_audit_ip_encode
#    ON trident_audit
#    USING btree
#    (ip_encode);
#
#  CREATE INDEX i_trident_audit_app_encode
#    ON trident_audit
#    USING btree
#    (app_encode);

# -- drop table trident_audit_finger
# CREATE TABLE trident_audit_finger
# (
#     date_time integer NOT NULL,                   --函数调用所在的日期
#     finger_print character varying(64) NOT NULL,  --函数调用的指纹
#     url character varying(800) NOT NULL,          --函数调用名称
#     times integer NOT NULL,                       --记录的次数
#     durable_time_avg integer NOT NULL,            --记录的平均调用时间
#     ip_encode character varying(40) NOT NULL,     --ip地址 md5
#     app_encode character varying(40) NOT NULL,    --应用名 md5
#     create_time timestamp with time zone NOT NULL DEFAULT now(),    --信息采集的时间
#     CONSTRAINT pk_trident_audit_finger_date_time_finger_print PRIMARY KEY (date_time, finger_print)
# );
#  CREATE INDEX i_trident_audit_finger_ip_encode
#    ON trident_audit_finger
#    USING btree
#    (ip_encode);
#
#  CREATE INDEX i_trident_audit_finger_app_encode
#    ON trident_audit_finger
#    USING btree
#    (app_encode);


# -- 指纹记录表， 每天每个指纹一条
# --drop table trident_audit_ip;
# --产生消息的主机ip和app对应关系表
# CREATE TABLE trident_audit_ip
# (
# 	audit_ip character varying(16) NOT NULL,
# 	audit_ip_encode character varying(40) NOT NULL,
#   audit_app_encode character varying(40) NOT NULL,
# 	CONSTRAINT pk_trident_audit_ip PRIMARY KEY (audit_ip_encode, audit_app_encode)
# );
#
# --drop table trident_audit_app;
# --产生消息的app表
# CREATE TABLE trident_audit_app
# (
# 	audit_app character varying(100) NOT NULL,
# 	audit_app_encode character varying(40) NOT NULL,
# 	CONSTRAINT pk_trident_audit_app PRIMARY KEY (audit_app_encode)
# );



__author__ = 'yuyichuan'

import pg
import json
import logging
import logging.config
import configCur
import hashlib
import datetime
import time

class DbPersisted:

    # 格式化时间
    def format_date(self, date_time, is_begin):
        # 认为是字符串格式的
        if date_time is not None and type(date_time) is str and len(date_time) >= 8:
            try:
                t_date_time = int(time.mktime(time.strptime(date_time, "%Y%m%d")))
            except Exception, e:
                # 异常则当作秒来使用
                t_date_time = date_time
        else:
            t_date_time = int(time.time())

        # is_begin 表示当天零点，否则为第二天零点
        dt = datetime.datetime.fromtimestamp(t_date_time if is_begin else (t_date_time + 60*60*24)).strftime("%Y%m%d%H%M%S")

        d_time = time.strptime(dt, '%Y%m%d%H%M%S')
        dd_time = datetime.datetime(*d_time[:3])
        i_et = int(time.mktime(dd_time.timetuple()))
        return i_et

    # 获取 logger
    def get_log(self):
        return logging.getLogger("dbPersisted")

    # 将接收到的json数据存入db
    def save_json_data(self, data_str):
        # json
        _url_ = "url"
        _async_ = "async"
        _begin_time_ = "begin"
        _end_time_ = "end"
        _host_name_ = "hostname"
        _ip_ = "ip"
        _app_ = "app"
        _status_ = "status"
        _children_ = "children"
        _attachments_ = "attachments"

        # insert_sql
        #                             "values(%s,       %s,            %s,              '%s',     '%s', '%s',  '%s',  '%s', '%s',        %s,         %s,       %s,           '%s',    '%s',      '%s');"
        insert_sql="insert into trident_audit(audit_id, root_audit_id, parent_audit_id, hostname, ip,   app,   async, url,  attachments, begin_time, end_time, durable_time, success, ip_encode, app_encode, layer_no, order_no, parent_order_nos) " \
                                      "values(%s, %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, %s, '%s', '%s', '%s', %s, %s, '%s');"

        data_json = json.loads(data_str, "utf-8")
        try:
            db = pg.connect(configCur.DB_NAME, configCur.DB_HOST, configCur.DB_PORT, None, None, configCur.DB_USER, configCur.DB_PWD)
        except Exception, e:
            # print e.args[0]
            self.get_log().error("to connect db failed, ret=%s" % e.args[0])
            return

        # 递归，批量处理
        def insert_data_batch(audit_data_list, root_Id, parent_Id, phost_name, pip, papp, pip_encode, papp_encode, reference_data, layer_no, parent_order_no):

            # 保存ip，允许失败
            def saveHostIp(ip, app):
                try:
                    hashapp_tp = hashlib.md5()
                    hashapp_tp.update(app)

                    haship_tp = hashlib.md5()
                    haship_tp.update(ip)

                    if db.query("select count(audit_ip) from trident_audit_ip where audit_ip_encode ='%s' and audit_app_encode='%s' " % (haship_tp.hexdigest(), hashapp_tp.hexdigest())).getresult()[0][0] == 0:
                        db.query("insert into trident_audit_ip(audit_ip, audit_ip_encode, audit_app_encode) values('%s', '%s', '%s')" % (ip, haship_tp.hexdigest(), hashapp_tp.hexdigest()))
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

            try:
                for i in range(0, len(audit_data_list)):
                    audit_data = audit_data_list[i]

                    cur_id = db.query("SELECT nextval('trident_audit_audit_id_seq');").getresult()[0][0]
                    begin_tp = audit_data[_begin_time_]
                    end_tp = audit_data[_end_time_]
                    elapse_tp = end_tp - begin_tp

                #第一条记录里，将ip， app，hsotname等都取到
                    if root_Id <= 0:
                        root_Id = cur_id #第一条记录，需要将root_id赋值
                        reference_data[1] = elapse_tp # 记录所花的时间
                        reference_data[2] = root_Id # 根节点id
                        reference_data[5] = begin_tp
                        reference_data[6] = audit_data[_url_]


                        hostname_tp = audit_data[_host_name_]
                        app_tp = audit_data[_app_]
                        ip_tp = audit_data[_ip_]

                        # 记录指纹数据：ip, app
                        reference_data[0].update(app_tp)
                        reference_data[0].update(ip_tp)

                        hashapp_tp = hashlib.md5()
                        hashapp_tp.update(app_tp)
                        app_encode = hashapp_tp.hexdigest()
                        reference_data[4] = app_encode

                        haship_tp = hashlib.md5()
                        haship_tp.update(ip_tp)
                        ip_encode = haship_tp.hexdigest()
                        reference_data[3] = ip_encode

                        saveHostIp(ip_tp, app_tp)
                        saveHostApp(app_tp)

                    else:
                        hostname_tp = phost_name
                        ip_tp = pip
                        ip_encode = pip_encode
                        app_tp = papp
                        app_encode = papp_encode
                        
                # 记录指纹数据：url
                    reference_data[0].update(audit_data[_url_])

                    if audit_data.has_key(_async_):
                        async_tp = 'async' if audit_data[_async_] else 'sync'
                    else:
                        async_tp = 'sync'

                    insert_data_sql = insert_sql % (cur_id,
                                                    root_Id,
                                                    parent_Id,
                                                    hostname_tp,
                                                    ip_tp,
                                                    app_tp,
                                                    async_tp,
                                                    audit_data[_url_],
                                                    ",".join(audit_data[_attachments_]) + " " if audit_data.has_key(_attachments_) else " ",
                                                    begin_tp,
                                                    end_tp,
                                                    elapse_tp,
                                                    audit_data[_status_],
                                                    ip_encode,
                                                    app_encode,
                                                    layer_no,
                                                    i,
                                                    parent_order_no if parent_order_no is not None else ''
                                                    )
                    self.get_log().debug(insert_data_sql)
                    db.query(insert_data_sql)

                # 有子节点， 递归调用
                    if audit_data.has_key(_children_) :
                        insert_data_batch(audit_data[_children_], root_Id, cur_id, hostname_tp, ip_tp, app_tp, ip_encode, app_encode, reference_data, layer_no + 1,
                                          "%s|%s" % (parent_order_no, i) if parent_order_no is not None else i)
            except Exception, e:
                # print e.args[0]
                self.get_log().error("insert record into trident_audit failed, ret=%s" % e.args[0])

        # 将指纹更新到相关的记录中
        def update_trident_audit_with_finger_print(reference_data):
            try:
                update_sql_str = "update trident_audit set finger_print ='%s' where root_audit_id=%s" % (reference_data[0].hexdigest(), reference_data[2])
                db.query(update_sql_str)
            except Exception, e:
                self.get_log().error("to update trident_audit with finger_print failed, ret=%s" % e.args[0])
            return

        # 将指纹和所花的时间作一个记录（直接计算平均值）
        def insert_record_finger_print(reference_data):
            i_et = self.format_date(reference_data[5]/1000, True)

            count_finger_print_sql_str = "select count(*) from trident_audit_finger where date_time=%s and finger_print='%s'" %(i_et, reference_data[0].hexdigest())

            insert_finger_print_sql_str = "insert into trident_audit_finger(date_time, finger_print, url, times, durable_time_avg, ip_encode, app_encode) " \
                                          "values(%s, '%s', '%s', %s, %s, '%s', '%s') " % (i_et, reference_data[0].hexdigest(), reference_data[6], 1, reference_data[1], reference_data[3], reference_data[4])

            update_finger_print_sql_str = "update trident_audit_finger set times = times +1 , durable_time_avg = (times * durable_time_avg + %s) / (times + 1) " \
                                          "where date_time=%s and finger_print='%s' " % (reference_data[1], i_et, reference_data[0].hexdigest())

            try:
                if db.query(count_finger_print_sql_str).getresult()[0][0] == 0:
                    db.query(insert_finger_print_sql_str)
                else:
                    db.query(update_finger_print_sql_str)
            except Exception, e:
                self.get_log().error("to insert trident_audit_finger with finger_print failed, ret=%s" % e.args[0])
                try:
                    db.query(update_finger_print_sql_str)
                except Exception, e:
                    self.get_log().error("and to update trident_audit_finger with finger_print failed, ret=%s" % e.args[0])

            return

        try:
            record_finger_print = hashlib.sha256()

            # 临时记录数据结构：[指纹, 所花时间, 根节点id, ip_encode, app_encode, begintime, url]
            reference_data = [record_finger_print, 0, 0, "ip", "app", 0, 0]

            insert_data_batch([data_json], 0, 0, None, None, None, None, None, reference_data, 0, None)

            update_trident_audit_with_finger_print(reference_data)

            insert_record_finger_print(reference_data)

        except Exception,e:
            print e.args[0]
            self.get_log().error("batch insert record into trident_audit failed, ret=%s" % e.args[0])
            db.close()
            return

    # db 查询操作
    def query_operation(self, op_mode='query_data_count'):

        db = pg.connect(configCur.DB_NAME, configCur.DB_HOST, configCur.DB_PORT, None, None, configCur.DB_USER, configCur.DB_PWD)

        # ##############################################################################################################
        # 指纹数据查询

        # 查询指纹记录条数
        def query_finger_count(date_time, ip_encode, app_encode):

            select_count_sql = "select count(*) from trident_audit_finger where %s" % _format_finger_data_sql(date_time, ip_encode, app_encode, 0, 0, False)
            self.get_log().debug(select_count_sql)

            return db.query(select_count_sql).getresult()[0][0]

        # 分页查询指纹数据
        def query_finger_data_page(date_time, ip_encode, app_encode, offset, limit, order_durable):

            # 格式化返回结果集合
            def trident_finger_list(query_result):
                retList = []
                rows = query_result.getresult()

                for row in rows:
                    item = {}
                    item['date_time'] = row[0]
                    item['finger_print'] = row[1]
                    item['url'] = row[2]
                    item['times'] = row[3]
                    item['elapse'] = row[4]
                    item['elapse_bar'] = (row[4] * 100) / configCur.BAR_MAX_TIME if row[4] < configCur.BAR_MAX_TIME else 100
                    item['ip_encode'] = row[5]
                    item['app_encode'] = row[6]
                    item['create_time'] = row[7]
                    retList.append(item)
                return retList

            select_finger_data_sql = "select * from trident_audit_finger where %s" % _format_finger_data_sql(date_time, ip_encode, app_encode, offset, limit, order_durable)
            self.get_log().debug(select_finger_data_sql)

            return trident_finger_list(db.query(select_finger_data_sql))

        # 格式化指纹数据查询条件
        def _format_finger_data_sql(date_time, ip_encode, app_encode, offset, limit, order_durable):
            start_time = datetime.datetime.fromtimestamp(self.format_date(date_time, True)).strftime("%Y-%m-%d")
            end_time = datetime.datetime.fromtimestamp(self.format_date(date_time, False)).strftime("%Y-%m-%d")

            where_str = " ip_encode='%s' and app_encode='%s' and create_time >= '%s' and create_time < '%s' " % (ip_encode, app_encode, start_time, end_time)
            where_str += " order by durable_time_avg desc " if order_durable else " "
            where_str += " limit %s offset %s " % (limit, offset) if limit > 0 else " "
            return where_str


        # ##############################################################################################################
        # 分组数据查询

        # 查询某个指纹下某一层的所有函数信息
        def query_transaction_data_group(layer_no, parent_order_no, finger_print, date_time):
            # 格式化返回数据
            def transaction_data_list(query_result):
                retList = []
                rows = query_result.getresult()

                for row in rows:
                    item = {}
                    item['ncount'] = row[0]
                    item['elapse_bar'] = (row[1] * 100) / configCur.BAR_MAX_TIME if row[1] < configCur.BAR_MAX_TIME else 100
                    item['elapse'] = row[1] if row[1] > 0  else " < 1 "
                    item['order_no'] = row[2]
                    item['async'] = row[3]
                    item['attachments'] = row[4]
                    item['parent_order_nos'] = "%s|%s" %(row[5], row[2]) if len(row[5]) > 0 else row[2]
                    item['url'] = row[6]
                    item['layer_no'] = row[7]
                    item['create_time'] = row[8]
                    retList.append(item)

                return retList

            start_time = datetime.datetime.fromtimestamp(self.format_date(date_time, True)).strftime("%Y-%m-%d")
            end_time = datetime.datetime.fromtimestamp(self.format_date(date_time, False)).strftime("%Y-%m-%d")

            query_data_sql = "select * from (" \
                                "select  count(*) as ncount, " \
                                    " cast(avg(durable_time) as integer) as avg_t, " \
                                    " order_no, " \
                                    " min(async) as async, " \
                                    " max(attachments) as attachments, " \
                                    " min(parent_order_nos) as parent_order_nos,	" \
                                    " min(url) as url, " \
                                    " min(layer_no) as layer_no," \
                                    " min(create_time) as create_time " \
                                    " from trident_audit where layer_no=%s and parent_order_nos='%s' and finger_print='%s' and create_time >= '%s' and create_time < '%s' group by order_no" \
                                ") as tp order by order_no" % (layer_no, parent_order_no, finger_print, start_time, end_time)

            self.get_log().debug(query_data_sql)

            return transaction_data_list(db.query(query_data_sql))

        # ##############################################################################################################
        # ip 和 app 查询

        # 查询ip
        def get_ips(app):

            # 格式化ip列表
            def ip_list(queryResult):
                retList = []
                rows = queryResult.getresult()

                for row in rows:
                    item = {}
                    item['audit_ip'] = row[0]
                    item['audit_ip_encode'] = row[1]
                    item['audit_app_encode'] = row[2]
                    retList.append(item)

                return retList

            return ip_list(db.query("select audit_ip, audit_ip_encode, audit_app_encode from trident_audit_ip where audit_app_encode='%s' " % app))

        # 查询app
        def get_apps():

            # 格式化app列表
            def app_list(queryResult):
                retList = []
                rows = queryResult.getresult()

                for row in rows:
                    item = {}
                    item['audit_app'] = row[0]
                    item['audit_app_encode'] = row[1]
                    retList.append(item)

                return retList

            return app_list(db.query('select audit_app, audit_app_encode from trident_audit_app'))

        ops = {'query_data_count':query_finger_count, 'query_finger_data':query_finger_data_page, 'query_transaction_data':query_transaction_data_group, 'query_ip':get_ips, 'query_app':get_apps}

        return ops[op_mode]

# main
if __name__ == '__main__':

    logging.config.fileConfig(configCur.LOG_CONFIG)
    dbPersisted = DbPersisted()
    # insert test
    # json_str1 = '{"attachments":[],"children":[{"attachments":[],"elapse":301,"status":"S","url":"info.kozz.web.Netiquette.netiquette"}],"elapse":328,"status":"S","url":"/home/netiquette.do"}'
    json_str ='{"app":"his-web","async":false,"begin":1420802609202,"children":[{"begin":1420802609202,"end":1420802609202,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"},{"begin":1420802609202,"children":[{"begin":1420802609202,"end":1420802609202,"status":"S","url":"com.tc.session.TCSession.access()"},{"begin":1420802609202,"end":1420802609202,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609202,"end":1420802609202,"status":"S","url":"com.tc.session.TCSessionManager.getSessionClient()"},{"begin":1420802609202,"children":[{"begin":1420802609202,"children":[{"begin":1420802609202,"end":1420802609202,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609202,"children":[{"begin":1420802609202,"end":1420802609202,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609202,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609202,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609203,"children":[{"begin":1420802609203,"children":[{"begin":1420802609203,"end":1420802609203,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609203,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609203,"end":1420802609203,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609203,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609203,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getAttribute(java.lang.String,java.lang.String)"}],"end":1420802609203,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609208,"end":1420802609208,"status":"S","url":"com.tcmc.his.biz.interceptor.CommInterreptor.preHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object)"},{"begin":1420802609208,"children":[{"begin":1420802609208,"end":1420802609208,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.getAnnotation(java.lang.Object)"}],"end":1420802609208,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.preHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object)"},{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO()"},{"begin":1420802609209,"children":[{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tc.common.web.interceptor.CustomPropertyEditorRegistrar$1(com.tc.common.web.interceptor.CustomPropertyEditorRegistrar)"}],"end":1420802609209,"status":"S","url":"com.tc.common.web.interceptor.CustomPropertyEditorRegistrar.registerCustomEditors(org.springframework.beans.PropertyEditorRegistry)"},{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tc.his.web.action.doctor.ReceptionAction.initBinder(org.springframework.web.bind.WebDataBinder)"},{"begin":1420802609209,"children":[{"begin":1420802609209,"children":[{"begin":1420802609209,"children":[{"begin":1420802609209,"children":[{"begin":1420802609209,"children":[{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tc.session.helper.CookieHelper.findCookie(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609209,"status":"S","url":"com.tc.session.helper.CookieHelper.findCookieValue(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609209,"status":"S","url":"com.tc.session.helper.CookieHelper.findSessionId(javax.servlet.http.HttpServletRequest)"}],"end":1420802609209,"status":"S","url":"com.tc.session.AbstractSessionManager.getRequestSessionId(javax.servlet.http.HttpServletRequest)"},{"begin":1420802609209,"children":[{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tc.session.AbstractSessionManager.getHttpSession(java.lang.String,javax.servlet.http.HttpServletRequest)"},{"begin":1420802609209,"children":[{"begin":1420802609209,"children":[{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609209,"children":[{"begin":1420802609209,"end":1420802609209,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609209,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609209,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609210,"children":[{"begin":1420802609210,"children":[{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609210,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getSession(java.lang.String)"},{"begin":1420802609210,"children":[{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.SessionMetaData.getLastAccessTime()"},{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.SessionMetaData.getMaxIdle()"}],"end":1420802609210,"status":"S","url":"com.tc.session.SessionMetaData.isValid()"},{"begin":1420802609210,"children":[{"begin":1420802609210,"children":[{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609210,"children":[{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609210,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.SessionMetaData.getId()"},{"begin":1420802609210,"end":1420802609210,"status":"S","url":"com.tc.session.SessionMetaData.setLastAccessTime(java.lang.Long)"},{"begin":1420802609212,"children":[{"begin":1420802609212,"children":[{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609212,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.updateSession(com.tc.session.SessionMetaData)"},{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.TCSession.setRequest(javax.servlet.http.HttpServletRequest)"}],"end":1420802609212,"status":"S","url":"com.tc.session.TCSessionManager.getHttpSession(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609212,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"}],"end":1420802609212,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession()"},{"begin":1420802609212,"children":[{"begin":1420802609212,"children":[{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.TCSession.access()"},{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.TCSessionManager.getSessionClient()"},{"begin":1420802609212,"children":[{"begin":1420802609212,"children":[{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609212,"children":[{"begin":1420802609212,"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609212,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609213,"children":[{"begin":1420802609213,"children":[{"begin":1420802609213,"end":1420802609213,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609213,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609213,"end":1420802609213,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609213,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609213,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getAttribute(java.lang.String,java.lang.String)"}],"end":1420802609213,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609213,"children":[{"begin":1420802609213,"children":[{"begin":1420802609213,"children":[{"begin":1420802609213,"children":[{"begin":1420802609213,"end":1420802609213,"status":"S","url":"com.tcmc.sso.commons.User.getUsername()"}],"end":1420802609213,"status":"S","url":"com.tcmc.sso.commons.User.getAccountId()"}],"end":1420802609213,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurAccountId()"},{"begin":1420802609213,"end":1420802609213,"status":"S","url":"com.tc.cache.CacheKeyGeneratorV2.generate(java.lang.Object,java.lang.reflect.Method,java.lang.Object[])"}],"end":1420802609214,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurUser()"},{"begin":1420802609214,"end":1420802609214,"status":"S","url":"com.tc.his.api.model.InternalUser.getHospitalId()"}],"end":1420802609214,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurHospitalId()"},{"begin":1420802609214,"children":[{"begin":1420802609214,"children":[{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaCode()"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaCode()"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaCode()"}],"end":1420802609218,"status":"S","url":"com.tcmc.his.biz.system.SystemParaBiz.getSystemParamByCode(java.lang.Integer,java.lang.Integer)"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaValue()"}],"end":1420802609218,"status":"S","url":"com.tcmc.his.biz.doctor.CommonReceptionActionBiz.checkRegisterIsNeed(java.lang.Integer)"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientTodo()"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientDone()"}],"end":1420802609218,"status":"S","url":"com.tc.his.web.action.doctor.ReceptionAction.listTodayInit(com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO,javax.servlet.http.HttpSession,javax.servlet.http.HttpServletRequest)"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.postHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,org.springframework.web.servlet.ModelAndView)"},{"begin":1420802609218,"end":1420802609218,"status":"S","url":"com.tcmc.his.biz.interceptor.CommInterreptor.postHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,org.springframework.web.servlet.ModelAndView)"},{"begin":1420802609219,"end":1420802609219,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"},{"begin":1420802609219,"children":[{"begin":1420802609219,"end":1420802609219,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609219,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609226,"end":1420802609226,"status":"S","url":"com.tcmc.his.biz.interceptor.CommInterreptor.preHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object)"},{"begin":1420802609226,"children":[{"begin":1420802609226,"end":1420802609226,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.getAnnotation(java.lang.Object)"}],"end":1420802609226,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.preHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object)"},{"begin":1420802609227,"end":1420802609227,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO()"},{"begin":1420802609227,"children":[{"begin":1420802609227,"end":1420802609227,"status":"S","url":"com.tc.common.web.interceptor.CustomPropertyEditorRegistrar$1(com.tc.common.web.interceptor.CustomPropertyEditorRegistrar)"}],"end":1420802609227,"status":"S","url":"com.tc.common.web.interceptor.CustomPropertyEditorRegistrar.registerCustomEditors(org.springframework.beans.PropertyEditorRegistry)"},{"begin":1420802609227,"end":1420802609227,"status":"S","url":"com.tc.his.web.action.doctor.ReceptionAction.initBinder(org.springframework.web.bind.WebDataBinder)"},{"begin":1420802609227,"end":1420802609227,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientDone()"},{"begin":1420802609228,"children":[{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tc.common.util.StrEscapeUtils.escapeHTMLTag(java.lang.String)"}],"end":1420802609228,"status":"S","url":"com.tc.common.web.interceptor.CustomPropertyEditorRegistrar$1.setAsText(java.lang.String)"},{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.setCheckPatientDone(java.lang.String)"},{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientTodo()"},{"begin":1420802609228,"children":[{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tc.common.util.StrEscapeUtils.escapeHTMLTag(java.lang.String)"}],"end":1420802609228,"status":"S","url":"com.tc.common.web.interceptor.CustomPropertyEditorRegistrar$1.setAsText(java.lang.String)"},{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.setCheckPatientTodo(java.lang.String)"},{"begin":1420802609228,"children":[{"begin":1420802609228,"children":[{"begin":1420802609228,"children":[{"begin":1420802609228,"children":[{"begin":1420802609228,"children":[{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tc.session.helper.CookieHelper.findCookie(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609228,"status":"S","url":"com.tc.session.helper.CookieHelper.findCookieValue(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609228,"status":"S","url":"com.tc.session.helper.CookieHelper.findSessionId(javax.servlet.http.HttpServletRequest)"}],"end":1420802609228,"status":"S","url":"com.tc.session.AbstractSessionManager.getRequestSessionId(javax.servlet.http.HttpServletRequest)"},{"begin":1420802609228,"children":[{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tc.session.AbstractSessionManager.getHttpSession(java.lang.String,javax.servlet.http.HttpServletRequest)"},{"begin":1420802609228,"children":[{"begin":1420802609228,"children":[{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609228,"children":[{"begin":1420802609228,"end":1420802609228,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609228,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609228,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609230,"children":[{"begin":1420802609230,"children":[{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609230,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getSession(java.lang.String)"},{"begin":1420802609230,"children":[{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.SessionMetaData.getLastAccessTime()"},{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.SessionMetaData.getMaxIdle()"}],"end":1420802609230,"status":"S","url":"com.tc.session.SessionMetaData.isValid()"},{"begin":1420802609230,"children":[{"begin":1420802609230,"children":[{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609230,"children":[{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609230,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.SessionMetaData.getId()"},{"begin":1420802609230,"end":1420802609230,"status":"S","url":"com.tc.session.SessionMetaData.setLastAccessTime(java.lang.Long)"},{"begin":1420802609232,"children":[{"begin":1420802609232,"children":[{"begin":1420802609232,"end":1420802609232,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609232,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609232,"end":1420802609232,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609232,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609232,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.updateSession(com.tc.session.SessionMetaData)"},{"begin":1420802609232,"end":1420802609232,"status":"S","url":"com.tc.session.TCSession.setRequest(javax.servlet.http.HttpServletRequest)"}],"end":1420802609232,"status":"S","url":"com.tc.session.TCSessionManager.getHttpSession(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609233,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"}],"end":1420802609233,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession()"},{"begin":1420802609233,"children":[{"begin":1420802609233,"children":[{"begin":1420802609233,"children":[{"begin":1420802609233,"children":[{"begin":1420802609233,"end":1420802609233,"status":"S","url":"com.tcmc.sso.commons.User.getUsername()"}],"end":1420802609233,"status":"S","url":"com.tcmc.sso.commons.User.getAccountId()"}],"end":1420802609233,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurAccountId()"},{"begin":1420802609233,"end":1420802609233,"status":"S","url":"com.tc.cache.CacheKeyGeneratorV2.generate(java.lang.Object,java.lang.reflect.Method,java.lang.Object[])"}],"end":1420802609233,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurUser()"},{"begin":1420802609233,"end":1420802609233,"status":"S","url":"com.tc.his.api.model.InternalUser.getParentHospitalId()"},{"begin":1420802609233,"end":1420802609233,"status":"S","url":"com.tc.his.api.model.InternalUser.getHospitalId()"},{"begin":1420802609233,"end":1420802609233,"status":"S","url":"com.tc.his.api.model.InternalUser.getUserId()"},{"begin":1420802609233,"end":1420802609233,"status":"S","url":"com.tc.his.api.model.InternalUser.getOfficeId()"},{"begin":1420802609233,"children":[{"begin":1420802609233,"children":[{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaCode()"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaCode()"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaCode()"}],"end":1420802609237,"status":"S","url":"com.tcmc.his.biz.system.SystemParaBiz.getSystemParamByCode(java.lang.Integer,java.lang.Integer)"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.his.api.model.SystemPara.getParaValue()"}],"end":1420802609237,"status":"S","url":"com.tcmc.his.biz.doctor.CommonReceptionActionBiz.checkRegisterIsNeed(java.lang.Integer)"},{"begin":1420802609237,"children":[{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609237,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSelectMyPatient()"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.setSelectMyPatient(java.lang.Integer)"},{"begin":1420802609237,"children":[{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.session.TCSession.access()"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.session.TCSessionManager.getSessionClient()"},{"begin":1420802609237,"children":[{"begin":1420802609237,"children":[{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609237,"children":[{"begin":1420802609237,"end":1420802609237,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609237,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609237,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609242,"children":[{"begin":1420802609242,"children":[{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609242,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609242,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609242,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.setAttribute(java.lang.String,java.lang.String,java.io.Serializable)"},{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tc.session.TCSession.fireHttpSessionBindEvent(java.lang.String,java.lang.Object)"}],"end":1420802609242,"status":"S","url":"com.tc.session.TCSession.setAttribute(java.lang.String,java.lang.Object)"},{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSelectMyPatient()"},{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getTriageFlag()"},{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getExaminationFlag()"},{"begin":1420802609242,"end":1420802609242,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSearchStr()"},{"begin":1420802609242,"end":1420802609249,"status":"S","url":"com.tcmc.his.biz.doctor.CommonReceptionActionBiz.countByDoctor(java.lang.Integer,java.lang.Integer,java.lang.Integer,java.lang.Integer,java.lang.Integer,java.lang.String,int,java.lang.Short,java.lang.Short)"},{"begin":1420802609249,"children":[{"begin":1420802609249,"end":1420802609249,"status":"S","url":"com.tc.his.utils.DateUtils.getToday()"},{"begin":1420802609249,"end":1420802609249,"status":"S","url":"com.tc.his.utils.DateUtils.getEndOfDay()"}],"end":1420802609255,"status":"S","url":"com.tcmc.his.biz.doctor.CommonReceptionActionBiz.countReceptionsByDoctor(java.lang.Integer,java.lang.Integer,java.lang.Integer,java.lang.Integer,java.lang.String,java.lang.Short)"},{"begin":1420802609255,"end":1420802609259,"status":"S","url":"com.tc.his.web.biz.system.InternalUserPropertyBiz.getUserRemindProperty(java.lang.Integer,java.lang.Integer,java.lang.Integer)"}],"end":1420802609259,"status":"S","url":"com.tc.his.web.action.doctor.ReceptionAction.listToday(com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO,javax.servlet.http.HttpSession,org.springframework.security.web.servletapi.SecurityContextHolderAwareRequestWrapper)"},{"begin":1420802609259,"end":1420802609259,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.postHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,org.springframework.web.servlet.ModelAndView)"},{"begin":1420802609259,"end":1420802609259,"status":"S","url":"com.tcmc.his.biz.interceptor.CommInterreptor.postHandle(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,org.springframework.web.servlet.ModelAndView)"},{"begin":1420802609265,"children":[{"begin":1420802609265,"children":[{"begin":1420802609265,"children":[{"begin":1420802609265,"children":[{"begin":1420802609265,"children":[{"begin":1420802609265,"end":1420802609265,"status":"S","url":"com.tc.session.helper.CookieHelper.findCookie(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609265,"status":"S","url":"com.tc.session.helper.CookieHelper.findCookieValue(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609265,"status":"S","url":"com.tc.session.helper.CookieHelper.findSessionId(javax.servlet.http.HttpServletRequest)"}],"end":1420802609265,"status":"S","url":"com.tc.session.AbstractSessionManager.getRequestSessionId(javax.servlet.http.HttpServletRequest)"},{"begin":1420802609265,"children":[{"begin":1420802609265,"end":1420802609265,"status":"S","url":"com.tc.session.AbstractSessionManager.getHttpSession(java.lang.String,javax.servlet.http.HttpServletRequest)"},{"begin":1420802609265,"children":[{"begin":1420802609265,"children":[{"begin":1420802609265,"end":1420802609265,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609265,"children":[{"begin":1420802609265,"end":1420802609265,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609265,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609265,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609266,"children":[{"begin":1420802609266,"children":[{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609266,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getSession(java.lang.String)"},{"begin":1420802609266,"children":[{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.SessionMetaData.getLastAccessTime()"},{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.SessionMetaData.getMaxIdle()"}],"end":1420802609266,"status":"S","url":"com.tc.session.SessionMetaData.isValid()"},{"begin":1420802609266,"children":[{"begin":1420802609266,"children":[{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609266,"children":[{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609266,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.SessionMetaData.getId()"},{"begin":1420802609266,"end":1420802609266,"status":"S","url":"com.tc.session.SessionMetaData.setLastAccessTime(java.lang.Long)"},{"begin":1420802609268,"children":[{"begin":1420802609268,"children":[{"begin":1420802609268,"end":1420802609268,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609268,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609268,"end":1420802609268,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609268,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609268,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.updateSession(com.tc.session.SessionMetaData)"},{"begin":1420802609268,"end":1420802609268,"status":"S","url":"com.tc.session.TCSession.setRequest(javax.servlet.http.HttpServletRequest)"}],"end":1420802609268,"status":"S","url":"com.tc.session.TCSessionManager.getHttpSession(java.lang.String,javax.servlet.http.HttpServletRequest)"}],"end":1420802609268,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"}],"end":1420802609268,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getScheme()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getServerPort()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientTodo()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientDone()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSearchStr()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSelectMyPatient()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getExaminationFlag()"},{"begin":1420802609269,"end":1420802609269,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getTriageFlag()"},{"begin":1420802609270,"end":1420802609270,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getScheme()"},{"begin":1420802609270,"end":1420802609270,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getServerPort()"},{"begin":1420802609270,"children":[{"begin":1420802609270,"children":[{"begin":1420802609270,"children":[{"begin":1420802609270,"children":[{"begin":1420802609270,"end":1420802609270,"status":"S","url":"com.tcmc.sso.commons.User.getUsername()"}],"end":1420802609270,"status":"S","url":"com.tcmc.sso.commons.User.getAccountId()"}],"end":1420802609270,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurAccountId()"},{"begin":1420802609270,"end":1420802609270,"status":"S","url":"com.tc.cache.CacheKeyGeneratorV2.generate(java.lang.Object,java.lang.reflect.Method,java.lang.Object[])"}],"end":1420802609270,"status":"S","url":"com.tcmc.sso.commons.LoginBiz.getCurUser()"},{"begin":1420802609270,"end":1420802609270,"status":"S","url":"com.tc.his.api.model.InternalUser.getUserId()"}],"end":1420802609271,"status":"S","url":"com.tcmc.his.biz.utils.SiteMapTag.doStartTag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientTodo()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCheckPatientDone()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSearchStr()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSelectMyPatient()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSelectMyPatient()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getSelectMyPatient()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getExaminationFlag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getExaminationFlag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getExaminationFlag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getTriageFlag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getTriageFlag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getTriageFlag()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getCardNum()"},{"begin":1420802609272,"end":1420802609272,"status":"S","url":"com.tcmc.his.biz.vo.doctor.DoctorReceptionSearchVO.getPatientName()"},{"begin":1420802609273,"end":1420802609273,"status":"S","url":"com.tcmc.his.biz.solr.HisProxyFactoryBean.getObjectType()"},{"begin":1420802609274,"end":1420802609274,"status":"S","url":"com.tcmc.his.biz.solr.HisProxyFactoryBean.getObjectType()"},{"begin":1420802609275,"end":1420802609275,"status":"S","url":"com.tcmc.his.biz.solr.HisProxyFactoryBean.getObjectType()"},{"begin":1420802609275,"children":[{"begin":1420802609275,"end":1420802609275,"status":"S","url":"com.tc.session.TCSession.access()"},{"begin":1420802609275,"end":1420802609275,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609275,"end":1420802609275,"status":"S","url":"com.tc.session.TCSessionManager.getSessionClient()"},{"begin":1420802609275,"children":[{"begin":1420802609275,"children":[{"begin":1420802609275,"end":1420802609275,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609275,"children":[{"begin":1420802609275,"end":1420802609275,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609275,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609275,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609291,"children":[{"begin":1420802609291,"children":[{"begin":1420802609291,"end":1420802609291,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609291,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609291,"end":1420802609291,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609291,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609291,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getAttribute(java.lang.String,java.lang.String)"}],"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609291,"children":[{"begin":1420802609291,"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609291,"children":[{"begin":1420802609291,"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609291,"children":[{"begin":1420802609291,"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609291,"children":[{"begin":1420802609291,"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609291,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609292,"children":[{"begin":1420802609292,"end":1420802609292,"status":"S","url":"com.tc.session.TCSession.access()"},{"begin":1420802609292,"end":1420802609292,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609292,"end":1420802609292,"status":"S","url":"com.tc.session.TCSessionManager.getSessionClient()"},{"begin":1420802609292,"children":[{"begin":1420802609292,"children":[{"begin":1420802609292,"end":1420802609292,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609292,"children":[{"begin":1420802609292,"end":1420802609292,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609292,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609292,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609293,"children":[{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609293,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609293,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609293,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getAttribute(java.lang.String,java.lang.String)"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609293,"children":[{"begin":1420802609293,"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609293,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609294,"children":[{"begin":1420802609294,"end":1420802609294,"status":"S","url":"com.tc.session.TCSession.access()"}],"end":1420802609294,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609294,"end":1420802609294,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getScheme()"},{"begin":1420802609294,"end":1420802609294,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getServerPort()"},{"begin":1420802609295,"children":[{"begin":1420802609295,"end":1420802609295,"status":"S","url":"com.tc.session.TCSession.access()"},{"begin":1420802609295,"end":1420802609295,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609295,"end":1420802609295,"status":"S","url":"com.tc.session.TCSessionManager.getSessionClient()"},{"begin":1420802609295,"children":[{"begin":1420802609295,"children":[{"begin":1420802609295,"end":1420802609295,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.activateObject(java.lang.Object)"},{"begin":1420802609295,"children":[{"begin":1420802609295,"end":1420802609295,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609295,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"}],"end":1420802609295,"status":"S","url":"com.tc.session.ZookeeperPoolManager.borrowObject()"},{"begin":1420802609296,"children":[{"begin":1420802609296,"children":[{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609296,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.validateObject(java.lang.Object)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.session.ZookeeperPoolableObjectFactory.passivateObject(java.lang.Object)"}],"end":1420802609296,"status":"S","url":"com.tc.session.ZookeeperPoolManager.returnObject(org.apache.zookeeper.ZooKeeper)"}],"end":1420802609296,"status":"S","url":"com.tc.session.zookeeper.ZookeeperSessionClient.getAttribute(java.lang.String,java.lang.String)"}],"end":1420802609296,"status":"S","url":"com.tc.session.TCSession.getAttribute(java.lang.String)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.afterCompletion(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,java.lang.Exception)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tcmc.his.biz.interceptor.CommInterreptor.afterCompletion(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,java.lang.Exception)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getRemoteAddr()"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tcmc.sso.commons.User.getUsername()"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.common.web.interceptor.SessionTokenHandlerInterceptor.afterCompletion(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,java.lang.Exception)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tcmc.his.biz.interceptor.CommInterreptor.afterCompletion(javax.servlet.http.HttpServletRequest,javax.servlet.http.HttpServletResponse,java.lang.Object,java.lang.Exception)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"},{"begin":1420802609296,"end":1420802609296,"status":"S","url":"com.tc.his.filter.ReverseProxyInfoFilter$ReverseProxyInfoRequest.getRemoteAddr()"},{"begin":1420802609297,"end":1420802609297,"status":"S","url":"com.tc.session.servlet.RemotableRequestWrapper.getSession(boolean)"},{"begin":1420802609297,"end":1420802609297,"status":"S","url":"com.tc.session.TCSession.getId()"},{"begin":1420802609297,"end":1420802609297,"status":"S","url":"com.tcmc.sso.commons.User.getUsername()"}],"end":1420802609297,"hostname":"puma","ip":"10.1.26.20","status":"S","url":"/tcgroup-his-web/reception/listTodayInit.do"}'

    dbPersisted.save_json_data(json_str)

    # query test
    try:
        dbPersisted.get_log().warn(dbPersisted.query_operation()(None, "281af57697156df10bc3f28458dad80f", "752a64b61ddb026c45e1158b4cd2d453"))
        dbPersisted.get_log().warn(dbPersisted.query_operation("query_finger_data")(None, "281af57697156df10bc3f28458dad80f", "752a64b61ddb026c45e1158b4cd2d453", 0, 10, True))
        dbPersisted.get_log().warn(dbPersisted.query_operation("query_transaction_data")(1, '0', "0ef8f7d3c8dba747a7be7513ec331e50f7d4b3ac83a8fcbf0c3810ef6ec695bf", None))
    except Exception, e:
        dbPersisted.get_log().error("operation failed, ret=%s" % e.args[0])


# End of dbPersisted.py

