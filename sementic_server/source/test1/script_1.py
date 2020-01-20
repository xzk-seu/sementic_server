import json


def result_extract():
    with open("first_0109.json", 'r') as fr:
        data = json.load(fr)['rows']

    for item in data:
        temp = dict()
        temp['uuid'] = item[0]
        temp['template_uuid'] = item[1]
        temp['sentence'] = item[2]


def main():
    with open("first_0111.json", 'r') as fr:
        data = json.load(fr)
        columns = data['columns']
        rows = data['rows']

    heads = list()
    result = list()
    for n, c in enumerate(columns):
        heads.append(c['name'])
    for item in rows:
        temp = dict()
        for n, h in enumerate(heads):
            temp[h] = item[n]
        result.append(temp)
    with open("test_result_0111.json", 'w') as fw:
        json.dump(result, fw)


if __name__ == '__main__':
    main()
