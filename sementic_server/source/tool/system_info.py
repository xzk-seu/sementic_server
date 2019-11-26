"""
@description: 系统配置文件，主要用于获取当前目录的基地址
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-26
@version: 0.0.1
"""
from os import getcwd
from os.path import abspath, join, pardir


class SystemInfo(object):
    """
    系统内部配置信息
    """

    _instance = None  # 单例模式-用来存放实例

    def __init__(self):
        """
        初始化
        """
        root_path = str(getcwd()).replace("\\", "/")
        if 'source' in root_path.split('/'):
            self.base_path = abspath(join(getcwd(), pardir, pardir))
        else:
            self.base_path = abspath(join(getcwd(), 'sementic_server'))


if __name__ == '__main__':
    si = SystemInfo()
    t = si.base_path
    print(t)
