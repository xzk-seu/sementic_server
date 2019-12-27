"""
@description: logger
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-26
@version: 0.0.1
"""

import logging
from logging import handlers

logger = logging.getLogger("server_log")
handler1 = logging.StreamHandler()
handler = logging.FileHandler(filename="sementic_server_log.log", encoding="utf-8")

# 每隔 1000 Byte 划分一个日志文件，备份文件为 3 个

maxBytes = 50 * 1024 * 1024
file_handler = handlers.RotatingFileHandler("sementic_server_log.log", mode="w", maxBytes=maxBytes, backupCount=30,
                                            encoding="utf-8")


logger.addHandler(handler1)
logger.addHandler(handler)
logger.addHandler(file_handler)
