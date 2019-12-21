import requests

url = "http://172.168.1.130:8000/ner/"

data = requests.get(url, {"sentence": "在烽火星空工作的程序员张小利昨晚和谁去了山东青岛"}).text
print(data)
