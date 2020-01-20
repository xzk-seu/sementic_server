"""
@description: 批量自测接口1
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""
import json


def read_result():
    with open("result_1.json", 'r') as fr:
        data = json.load(fr)
    for item in data:
        if item['status'] != "200" and item['status'] != "201":
            print(item)
    err = [x for x in data if x['status'] != "200" and x['status'] != "201"]
    print(len(err), len(data))
    for item in data:
        if item['status'] == "201":
            print(item)
    err = [x for x in data if x['status'] == "201"]
    print(len(err), len(data))


if __name__ == '__main__':
    read_result()
