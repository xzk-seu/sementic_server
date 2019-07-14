"""
@description: 测试代码
@author: Cui Rui long
@email: xiaocuikindle@163.com
@time: 2019-07-02
@version: 0.0.1
"""

import os

from pprint import pprint
from sementic_server.source.recommend.recommend_server import RecommendServer

if __name__ == '__main__':
    recommend = RecommendServer()
    test_data_file = os.path.join(recommend.base_path, 'data', 'test_recommend_data',
                                  '1001711081640003790000917493.json')
    key = "2"
    # recommend.save_data_to_redis(data_file=test_data_file, key=key)
    data = recommend.load_data_from_redis(key=key)
    recommend.degree_count(data=data)
    results = recommend.get_recommend_result(key=2, top_num=10)
    pprint(results)
