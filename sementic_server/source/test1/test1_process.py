import json
import yaml


def show_form(data):
    for line in data:
        print(line)
        print("====================")
        for n, i in enumerate(line):
            print(n, i)
        break


def get_err_list(data):
    err = list()
    for line in data:
        if line[5] != "通过":
            err.append(line)
    print(len(err))
    with open('err.json', 'w') as fw:
        json.dump(err, fw)


def get_null_list(data):
    err = list()
    for line in data:
        if not line[5]:
            err.append(line)
    print(len(err))
    with open('null.json', 'w') as fw:
        json.dump(err, fw)

    with open('400.txt', 'w') as fw:
        for line in err:
            fw.write(line[2]+'\n')


def identifier_extract(data):
    identifier = dict()
    for line in data:
        if not line or not line[3]:
            continue
        temp_dict = json.loads(line[3].replace("'", "\""))
        for k, v in temp_dict.items():
            if "标识" in k:
                print(k, v)
                identifier.setdefault(k, set())
                identifier[k].add(v['value'])
    print(len(identifier))
    print(identifier)
    new_ques = dict()
    for k, v in identifier.items():
        new_ques[k] = list(v)
    with open("identifier.yml", 'w') as fw:
        yaml.dump(new_ques, fw, allow_unicode=True)


def quesword_extract(data):
    quesword = dict()
    for line in data:
        if not line or not line[3]:
            continue
        temp_dict = json.loads(line[3].replace("'", "\""))
        for k, v in temp_dict.items():
            if "疑问词" in k:
                print(k, v)
                quesword.setdefault(k, set())
                quesword[k].add(v['value'])
    print(len(quesword))
    print(quesword)
    new_ques = dict()
    for k, v in quesword.items():
        new_ques[k] = list(v)
    with open("quesword.yml", 'w') as fw:
        yaml.dump(new_ques, fw, allow_unicode=True)


def main():
    with open("first.json", 'r') as fr:
        data = json.load(fr)['rows']

    print(len(data))


if __name__ == '__main__':
    main()

