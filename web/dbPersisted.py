# !/usr/bin/python
# -*- coding: UTF-8 -*-

# Filename:dbPersisted.py

# 将监控消息内容存入关系数据库中，存放的表结构如下：
# --drop table trident_audit;
# --drop table trident_audit_ip;
# --drop table trident_audit_app;
#
# CREATE TABLE trident_audit
# (
#   audit_id serial NOT NULL,
#   root_audit_id integer NOT NULL,
#   parent_audit_id integer NOT NULL,
#   hostname character varying(50) NOT NULL,
#   ip character varying(100) NOT NULL,
#   app character varying(100) NOT NULL,
#   ip_encode character varying(40) NOT NULL,
#   app_encode character varying(40) NOT NULL,
#   async character varying(20) NOT NULL,
#   url character varying(800) NOT NULL,
#   attachments character varying(800),
#   begin_time bigint NOT NULL,
#   end_time bigint NOT NULL,
#   durable_time integer NOT NULL,
#   success character varying(6) NOT NULL,
#   create_time timestamp with time zone NOT NULL DEFAULT now(),
#   CONSTRAINT pk_trident_audit PRIMARY KEY (audit_id)
# );
#
# CREATE INDEX i_trident_audit_root_audit_id
#   ON trident_audit
#   USING btree
#   (root_audit_id);
#
# CREATE INDEX i_trident_audit_root_durable_time
#   ON trident_audit
#   USING btree
#   (durable_time);
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

# CREATE TABLE trident_audit_ip
# (
# 	audit_ip character varying(16) NOT NULL,
# 	audit_ip_encode character varying(40) NOT NULL,
#   audit_app_encode character varying(40) NOT NULL,
# 	CONSTRAINT pk_trident_audit_ip PRIMARY KEY (audit_ip_encode, audit_app_encode)
# );
#
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

class DbPersisted:

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
        insert_sql="insert into trident_audit(audit_id, root_audit_id, parent_audit_id, hostname, ip,   app,   async, url,  attachments, begin_time, end_time, durable_time, success, ip_encode, app_encode) " \
                                      "values(%s, %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, %s, '%s', '%s', '%s');"

        data_json = json.loads(data_str, "utf-8")
        try:
            db = pg.connect(configCur.DB_NAME, configCur.DB_HOST, configCur.DB_PORT, None, None, configCur.DB_USER, configCur.DB_PWD)
        except Exception, e:
            # print e.args[0]
            self.get_log().error("to connect db failed, ret=%s" % e.args[0])
            return

        # 递归，批量处理
        def insert_data_batch(audit_data_list, root_Id, parent_Id, phost_name, pip, papp, pip_encode, papp_encode):
            try:
                for audit_data in audit_data_list:

                    cur_id = db.query("SELECT nextval('trident_audit_audit_id_seq');").getresult()[0][0]
                    if root_Id <= 0:#第一条记录里，将ip， app，hsotname等都取到
                        hostname_tp = audit_data[_host_name_]
                        app_tp = audit_data[_app_]
                        ip_tp = audit_data[_ip_]

                        hashapp_tp = hashlib.md5()
                        hashapp_tp.update(app_tp)
                        app_encode = hashapp_tp.hexdigest()

                        haship_tp = hashlib.md5()
                        haship_tp.update(ip_tp)
                        ip_encode = haship_tp.hexdigest()

                        root_Id = cur_id

                        self.saveHostIp(ip_tp, app_tp, db)
                        self.saveHostApp(app_tp, db)

                    else:
                        hostname_tp = phost_name
                        ip_tp = pip
                        ip_encode = pip_encode
                        app_tp = papp
                        app_encode = papp_encode
                        
                    if parent_Id < 0:
                        parent_Id = 0

                    elapse_tp = audit_data[_end_time_] - audit_data[_begin_time_]
                    if audit_data.has_key(_async_):
                        async_tp = 'async' if audit_data[_async_] else 'sync'
                    else:
                        async_tp = 'sync'

                    begin_tp = audit_data[_begin_time_]
                    end_tp = audit_data[_end_time_]

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
                                                    app_encode
                                                    )
                    self.get_log().debug(insert_data_sql)
                    db.query(insert_data_sql)

                    if audit_data.has_key(_children_) :
                        insert_data_batch(audit_data[_children_], root_Id, cur_id, hostname_tp, ip_tp, app_tp, ip_encode, app_encode)
            except Exception, e:
                # print e.args[0]
                self.get_log().error("insert record into trident_audit failed, ret=%s" % e.args[0])

        try:
            insert_data_batch([data_json], 0, 0, None, None, None, None, None)
        except Exception,e:
            print e.args[0]
            self.get_log().error("batch insert record into trident_audit failed, ret=%s" % e.args[0])
            db.close()
            return

    # 保存ip，允许失败
    def saveHostIp(self, ip, app, db):
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
    def saveHostApp(self, app, db):
        try:
            hashapp_tp = hashlib.md5()
            hashapp_tp.update(app)

            if db.query("select count(audit_app) from trident_audit_app where audit_app_encode ='%s'" % hashapp_tp.hexdigest()).getresult()[0][0] == 0:
                db.query("insert into trident_audit_app(audit_app, audit_app_encode) values('%s', '%s')" % (app, hashapp_tp.hexdigest()))
        except Exception, e:
            self.get_log().warn("save audit_app failed, ret=%s" % e.args[0])
        return


    # db 查询操作
    def queryOperation(self, op_mode='query_data_count'):

        db = pg.connect(configCur.DB_NAME, configCur.DB_HOST, configCur.DB_PORT, None, None, configCur.DB_USER, configCur.DB_PWD)

        # 组装sql语句
        def _format_query(root_id, parent_id, method_name, start_time, end_time, app, ip):
            # parent_id 必须提供
            where_str = " parent_audit_id = %s " % parent_id if parent_id > 0 else " parent_audit_id = 0 "

            where_str += " and root_audit_id = %s " % root_id if root_id > 0 else " "
            where_str += " and create_time >= '%s' " % start_time if start_time is not None else " "
            where_str += " and create_time <= '%s' " % end_time if end_time is not None else " "
            where_str += " and app_encode ='%s'" % app if app is not None else " "
            where_str += " and ip_encode ='%s'" % ip if ip is not None else " "
            where_str += " and method_name like '%%%s%%' " % method_name if method_name is not None else " "

            return where_str

        # 分页查询数据
        def queryData(root_id, parent_id, method_name, offset, limit, order_durable, start_time, end_time, app, ip):
            if offset < 0:
                offset = 0

            if limit < 0:
                limit = 0

            where_str = _format_query(root_id, parent_id, method_name, start_time, end_time, app, ip)
            where_str += " order by durable_time desc " if order_durable else " order by audit_id desc "
            where_str += " limit %s offset %s " % (limit, offset) if limit > 0 else " "
            where_str_2 = " select * from trident_audit where " + where_str
            self.get_log().debug(where_str_2)

            return trident_list(db.query(where_str_2))

        # 查询记录数量
        def queryDataCount(root_id, parent_id, method_name, start_time, end_time, app, ip):
            where_str = " select count(*) from trident_audit where " + _format_query(root_id, parent_id, method_name, start_time, end_time, app, ip)
            self.get_log().debug(where_str)

            return db.query(where_str).getresult()[0][0]

        # 查询ip
        def getIps(app):
            return ip_list(db.query("select audit_ip, audit_ip_encode, audit_app_encode from trident_audit_ip where audit_app_encode='%s' " % app))

        # 查询app
        def getApps():
            return app_list(db.query('select audit_app, audit_app_encode from trident_audit_app'))

        # 将查询结果格式化成列表
        def trident_list(queryResult):
            retList = []
            rows = queryResult.getresult()

            for row in rows:
                item = {}
                item['audit_id'] = row[0]
                item['root_audit_id'] = row[1]
                item['parent_audit_id'] = row[2]
                item['hostname'] = row[3]
                item['ip'] = row[4]
                item['app'] = row[5]
                item['ip_encode'] = row[6]
                item['app_encode'] = row[7]
                item['async'] = row[8]
                item['url'] = row[9]
                item['attachments'] = row[10]
                item['begin_time'] = row[11]
                item['end_time'] = row[12]
                item['elapse_bar'] = (row[13] * 100) / configCur.BAR_MAX_TIME if row[13] < configCur.BAR_MAX_TIME else 100
                item['elapse'] = row[13] if row[13] > 0  else " < 1 "
                item['status'] = row[14]
                item['create_time'] = row[15]
                retList.append(item)

            return retList

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

        ops = {'query_data_count':queryDataCount, 'query_data':queryData, 'query_ip':getIps, 'query_app':getApps}

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
        dbPersisted.get_log().warn(dbPersisted.queryOperation()(0, 0, None, None, None, None))
        dbPersisted.get_log().warn(dbPersisted.queryOperation("query_data")(0, 0, None, 0, 30, True, None, None, None, None))
    except Exception, e:
        dbPersisted.get_log().error("operation failed, ret=%s" % e.args[0])


# End of dbPersisted.py

