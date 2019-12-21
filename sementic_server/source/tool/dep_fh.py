import requests
import json


def get_dep(sentence):
    url = 'http://120.132.109.87:10088/jfycfx'
    if sentence[-1] == '？':
        # 去除问句末尾的问号
        sentence = sentence[:-1]

    resp = requests.get(url, params={'text': sentence})
    data = json.loads(resp.text)
    return data


if __name__ == '__main__':
    # sent = "烽火科技的张经理是谁"
    sent = "烽火科技大厦的张三"
    t = get_dep(sent)
    print(t)
    with open('test.json', 'w') as fw:
        json.dump(t['data'], fw)
