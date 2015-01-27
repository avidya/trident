#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Filename:Config.py

__author__ = 'yuyichuan'

# log config
LOG_CONFIG = 'logging.conf'

# db config
DB_NAME = 'stat_monitor'
DB_HOST = '10.1.121.179'
DB_PORT = 1949
DB_USER = 'postgres'
DB_PWD = '123456'

# stomp config
STOMP_HOST = '10.1.11.214'
STOMP_PORT = 61613
# 性能消息队列
TRANSACTION_DESTINATION = '/queue/call-info'

# 系统信息队列
STATUS_INFO_DESTINATION = '/queue/heartbeat-info'

# message min length
MIN_MESSAGE_LEN = 10

# http
HTTP_PORT = 9090
HTTP_HOST = '0.0.0.0'


# 时间条最大值（ms）
BAR_MAX_TIME = 3000

# page info
PAGE_SIZE = 20

# 列表的背景颜色
table_colors =('#2f7ed8','#efd4e4','#8bbc21','#ece9b2','#1aadce','#9dd4fd','#d995bd','#77a1e5','#d8d260','#a6c96a')

# 生成的柱状图存放的地址
BAR_PATH = './bar_tp'
