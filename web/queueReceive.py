# !/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:queueReceive.py

# 从消息队列接收监控消息,并且将搜到的消息持久到db中

__author__ = 'yuyichuan'

from dbPersisted import DbPersisted
from stomp import StatsListener, WaitingListener
import stomp
import time
import logging
import logging.config
import configCur

class StatInfoListener(StatsListener, WaitingListener):

    def __init__(self, receipt, subscribe_id):
        StatsListener.__init__(self)
        WaitingListener.__init__(self, "%s%s" % (receipt, subscribe_id))
        self.dbPersisted = DbPersisted()
        self.id = subscribe_id


    def on_message(self, headers, message):
        get_log().info('received a message: %s' % message)
        if len(message) < configCur.MIN_MESSAGE_LEN:
            get_log().warn('discard message:%s' % message)
            self.on_receipt(headers, message)
        else:
            self.dbPersisted.save_json_data(message)

def get_log():
        return logging.getLogger("statInfoListener")

if __name__ == '__main__':

    logging.config.fileConfig(configCur.LOG_CONFIG)

    statInfoListener = StatInfoListener("DISCONNECT", 1)

    conn = stomp.Connection(host_and_ports=[(configCur.STOMP_HOST, configCur.STOMP_PORT)])
    conn.set_listener('fisher', statInfoListener)
    conn.start()
    conn.connect(wait=True)
    conn.subscribe(destination=configCur.DESTINATION, id=statInfoListener.id, ack="auto")

    statInfoListener.wait_on_receipt()
    conn.disconnect()
    get_log().info("disconnected from queue and exited:%s" % time.gmtime(time.time()))

