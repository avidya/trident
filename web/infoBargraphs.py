# !/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'yuyichuan'


from pyx import *
import hashlib
import logging
import logging.config
from Config import *
import os


class Bargraphs:

    # x轴
    _xname = 'xname'

    # y轴
    _y = 'y'

    # 获取 logger
    def get_log(self):
        return logging.getLogger("bargraphs")

    # 画图
    def create_bar_png(self, _data_dict, _file_name = None, _width = None, _height = None, force_create = False):
        self.get_log().info(_data_dict)

        if _data_dict is None or len(_data_dict) < 1:
            self.get_log().error("用来生成图形的数据必须提供：%s" % _data_dict)
            return None

        if _file_name is None:
            hash_file_name = hashlib.md5()
            hash_file_name.update(reduce(lambda s, a: "%s,%d" % (s, a), _data_dict[self._xname], " "))
            hash_file_name.update(reduce(lambda s, a: "%s,%d" % (s, a), _data_dict[self._y], " "))

            _file_name = "%s.png" % hash_file_name.hexdigest()

        _full_file_name = "%s/%s.png" % (BAR_PATH, _file_name)
        _full_file_name_data = "%s/%s.txt" % (BAR_PATH, _file_name)
        self.get_log().debug("临时文件名：%s" % _full_file_name)
        self.get_log().debug("临时文件名：%s" % _full_file_name_data)

        if os.path.exists(_full_file_name_data) and force_create:
            os.remove(_full_file_name_data)

        if os.path.exists(_full_file_name) and force_create:
            os.remove(_full_file_name)

        outfile = open(_full_file_name_data, "w")
        outfile.writelines(_data_dict)
        outfile.close()

        # 若存在则直接返回
        if not os.path.exists(_full_file_name) or force_create:
            if _width is None:
                _width = len(_data_dict) if len(_data_dict) > 8 else 8

            _painter = graph.axis.painter.bar(nameattrs=[trafo.rotate(0), text.halign.right], innerticklength=0.1)
            _axis = graph.axis.bar(painter = _painter)

            g = graph.graphxy(width = _width, height = _height, x = _axis)
            g.plot(graph.data.file(_full_file_name_data, y = 1, xname = 2), [graph.style.bar()])
            g.writeGSfile(_full_file_name)

        return _file_name

# main
if __name__ == '__main__':

    logging.config.fileConfig(LOG_CONFIG)

    __data_dict = {
        "y" : [1.0, 3.0, 8.0, 13.0, 18.0, 21.0, 23.0, 23.0, 19.0, 13.0, 6.0, 2.0, 1.0, 3.0, 8.0, 13.0, 18.0, 21.0, 23.0, 23.0, 19.0, 13.0, 6.0, 2.0],
        "xname" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    }

    _bargraphs = Bargraphs()

    print(_bargraphs.create_bar_png(__data_dict, None, None, None, True))