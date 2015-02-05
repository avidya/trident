#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:QueueReceiver.py
from time import sleep

# 从消息队列接收监控消息,并且将搜到的消息持久到db中

__author__ = 'yuyichuan'

from transactionPersisted import DbPersisted
from heartbeatPersisted import HeartBeatPgPersisted
from stomp import StatsListener, WaitingListener
import stomp
import threading
import time
import logging
import logging.config
from Config import *

class StatInfoListener(StatsListener, WaitingListener):

    def __init__(self, receipt, subscribe_id, persister):
        StatsListener.__init__(self)
        WaitingListener.__init__(self, "%s%s" % (receipt, subscribe_id))
        self.dbPersisted = persister
        self.id = subscribe_id


    def on_message(self, headers, message):
        get_log().info('received a message: %s' % message)
        if len(message) < MIN_MESSAGE_LEN:
            get_log().warn('discard message:%s' % message)
            self.on_receipt(headers, message)
        else:
            self.dbPersisted.save_json_data(message)

def get_log():
        return logging.getLogger("statInfoListener")

if __name__ == '__main__':

    logging.config.fileConfig(LOG_CONFIG)

    # 启动多个消费者
    for i in xrange(0, TRANSACTION_THREAD):
        callInfoListener = StatInfoListener("DISCONNECT", i, DbPersisted())

        conn = stomp.Connection(host_and_ports=[(STOMP_HOST, STOMP_PORT)])
        conn.set_listener('fisher%s'% i, callInfoListener)
        conn.start()
        conn.connect(wait=True)
        conn.subscribe(destination=TRANSACTION_DESTINATION, id=callInfoListener.id, ack="auto")
        t1 = threading.Thread(target=callInfoListener.wait_on_receipt)
        t1.daemon = True
        t1.start()
        get_log().warn('启动Listener:%s%s' % ('callInfoListener', i))
        sleep(1)
#     callInfoListener.wait_on_receipt()
    
    heartBeatInfoListener = StatInfoListener("DISCONNECT", 2, HeartBeatPgPersisted())

    conn2 = stomp.Connection(host_and_ports=[(STOMP_HOST, STOMP_PORT)])
    conn2.set_listener('fisher2', heartBeatInfoListener)
    conn2.start()
    conn2.connect(wait=True)
    conn2.subscribe(destination=STATUS_INFO_DESTINATION, id=heartBeatInfoListener.id, ack="auto")  
    t2 = threading.Thread(target=heartBeatInfoListener.wait_on_receipt)
    t2.daemon = True
    t2.start()
    get_log().warn('启动Listener:%s%s' % ('heartBeatInfoListener'))
#     heartBeatInfoListener.wait_on_receipt()
    
#     conn.disconnect()
#     conn2.disconnect()
    while True:
        sleep(1000)
